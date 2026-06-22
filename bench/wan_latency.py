"""Emulated-WAN decision-latency study (Bucket D').

Drives the decision communication patterns (single hop, wait-for-majority, wait-for-all-R) over the
peer containers behind a Toxiproxy proxy that injects per-link latency, jitter, and probabilistic loss,
and reports the decision-latency TAILS (p50/p95/p99/p99.9) per pattern and WAN profile. This upgrades
the trivial localhost medians to real tails over real (proxied) sockets.

HONEST SCOPE (N6): single-host emulation -- containers share the host CPU/NIC, so this is emulated WAN,
not a geo-distributed deployment; we report the relative ordering of the tiers and the tail behaviour,
not geo-distributed absolute throughput.

Setup:  docker compose -f docker/docker-compose.wan.yml up -d --build
Run:    PYTHONPATH=src:. python -m bench.wan_latency
Output: results/tables/wan_latency.csv  (STATUS: validated only after a stable repeat run)
"""
from __future__ import annotations

import asyncio
import csv
import time
from pathlib import Path
from statistics import quantiles

import httpx

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables" / "wan_latency.csv"
CONTROL = "http://127.0.0.1:8474"
R = 5
PROXY = [f"http://127.0.0.1:{18000 + i}" for i in range(R)]
N = 800           # samples per (profile, pattern) -- solid p50/p95/p99, indicative p99.9
WARMUP = 50
CLIENT_TIMEOUT = 1.0   # a 1 s decision deadline: dropped requests (loss) count as a 1 s tail sample

# WAN profiles: (name, base latency ms, jitter ms, connection-loss fraction)
PROFILES = [
    ("lan", 1, 0, 0.0),
    ("regional", 20, 5, 0.0),
    ("wan", 80, 20, 0.0),
    ("wan-lossy", 80, 20, 0.02),
]


async def _api(client: httpx.AsyncClient, method: str, path: str, json=None):
    r = await client.request(method, f"{CONTROL}{path}", json=json)
    if r.status_code >= 400 and method != "DELETE":
        raise RuntimeError(f"toxiproxy {method} {path} -> {r.status_code}: {r.text}")
    return r


async def _setup_proxies(client: httpx.AsyncClient) -> None:
    """Create one proxy per peer (idempotent: delete then recreate)."""
    for i in range(R):
        name = f"peer{i}"
        await _api(client, "DELETE", f"/proxies/{name}")
        await _api(client, "POST", "/proxies", json={
            "name": name, "listen": f"0.0.0.0:{18000 + i}",
            "upstream": f"peer{i}:8000", "enabled": True})


async def _set_profile(client: httpx.AsyncClient, latency: int, jitter: int, loss: float) -> None:
    """Replace the toxics on every proxy with this WAN profile."""
    for i in range(R):
        name = f"peer{i}"
        for tox in ("lat", "loss"):                 # clear previous
            await _api(client, "DELETE", f"/proxies/{name}/toxics/{tox}")
        await _api(client, "POST", f"/proxies/{name}/toxics", json={
            "name": "lat", "type": "latency", "stream": "downstream",
            "attributes": {"latency": latency, "jitter": jitter}})
        if loss > 0:
            await _api(client, "POST", f"/proxies/{name}/toxics", json={
                "name": "loss", "type": "timeout", "stream": "downstream",
                "toxicity": loss, "attributes": {"timeout": 0}})   # toxicity fraction -> dropped conns


async def _one_hop(client: httpx.AsyncClient) -> None:
    await client.get(f"{PROXY[0]}/view/p0")


async def _majority(client: httpx.AsyncClient) -> None:
    k = R // 2 + 1
    tasks = [asyncio.ensure_future(client.get(f"{PROXY[i]}/view/p{i}")) for i in range(R)]
    done = 0
    for fut in asyncio.as_completed(tasks):
        try:
            await fut
        except Exception:
            pass
        done += 1
        if done >= k:
            break
    for t in tasks:
        t.cancel()


async def _fan_out(client: httpx.AsyncClient) -> None:
    await asyncio.gather(*[client.get(f"{PROXY[i]}/view/p{i}") for i in range(R)],
                         return_exceptions=True)


PATTERNS = [("1-hop", _one_hop), ("majority", _majority), ("R-fan-out", _fan_out)]


def _tails(samples: list[float]) -> dict:
    cuts = quantiles(samples, n=1000, method="inclusive")
    return {"p50_ms": round(cuts[499], 3), "p95_ms": round(cuts[949], 3),
            "p99_ms": round(cuts[989], 3), "p999_ms": round(cuts[998], 3)}


async def _wait_ready(client: httpx.AsyncClient) -> None:
    for _ in range(100):
        try:
            if (await client.get(f"{CONTROL}/version")).status_code == 200:
                return
        except Exception:
            await asyncio.sleep(0.2)
    raise RuntimeError("toxiproxy control API not ready on :8474")


async def _bench() -> list[dict]:
    rows = []
    async with httpx.AsyncClient(timeout=CLIENT_TIMEOUT) as client:
        await _wait_ready(client)
        await _setup_proxies(client)
        for pname, latency, jitter, loss in PROFILES:
            await _set_profile(client, latency, jitter, loss)
            for label, fn in PATTERNS:
                for _ in range(WARMUP):
                    try:
                        await fn(client)
                    except Exception:
                        pass
                samples = []
                for _ in range(N):
                    t0 = time.perf_counter()
                    try:
                        await fn(client)
                    except Exception:
                        pass     # dropped/timed-out request under loss: record the elapsed (~timeout) as the sample
                    samples.append((time.perf_counter() - t0) * 1000.0)
                row = {"profile": pname, "pattern": label, "latency_ms": latency,
                       "jitter_ms": jitter, "loss": loss, "n": N, **_tails(samples)}
                rows.append(row)
                print(f"  [{pname:9s}] {label:10s} "
                      f"p50={row['p50_ms']:.1f} p99={row['p99_ms']:.1f} p99.9={row['p999_ms']:.1f} ms",
                      flush=True)
    return rows


def main() -> None:
    rows = asyncio.run(_bench())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wan latency -> {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
