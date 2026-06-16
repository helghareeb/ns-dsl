"""Measure decision latency against the REAL Dockerized peer containers.

Confirms the localhost latency tiers hold under an actual container deployment: hits the peer
containers (host ports 8000..8004) over real HTTP and times a single-hop read and a full
$R$-peer fan-out. Run after ``docker compose -f docker/docker-compose.yml up -d --build``.

Run:  PYTHONPATH=src:. python -m bench.docker_latency
"""
from __future__ import annotations

import asyncio
import csv
import time
from pathlib import Path
from statistics import quantiles

import httpx

OUT = Path(__file__).resolve().parents[1] / "results" / "tables" / "latency_docker.csv"
PEERS = [f"http://127.0.0.1:{8000 + i}" for i in range(5)]
RTT_MS = 5.0
N = 200


async def _wait(client: httpx.AsyncClient) -> None:
    for url in PEERS:
        for _ in range(100):
            try:
                if (await client.get(f"{url}/health")).status_code == 200:
                    break
            except Exception:
                await asyncio.sleep(0.1)
        else:
            raise RuntimeError(f"container not ready: {url}")


async def _one_hop(client: httpx.AsyncClient) -> None:
    await client.get(f"{PEERS[0]}/view/p0", params={"rtt": RTT_MS})


async def _fan_out(client: httpx.AsyncClient) -> None:
    await asyncio.gather(*[client.get(f"{u}/view/p{i}", params={"rtt": RTT_MS})
                           for i, u in enumerate(PEERS)])


async def _bench() -> list[dict]:
    rows = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        await _wait(client)
        for label, fn in [("1-hop (centralized-like)", _one_hop),
                          ("R-fan-out (neutro-like)", _fan_out)]:
            for _ in range(20):
                await fn(client)
            samples = []
            for _ in range(N):
                t0 = time.perf_counter()
                await fn(client)
                samples.append((time.perf_counter() - t0) * 1000.0)
            cuts = quantiles(samples, n=100, method="inclusive")
            rows.append({"pattern": label, "n": N, "p50_ms": round(cuts[49], 3),
                         "p95_ms": round(cuts[94], 3), "p99_ms": round(cuts[98], 3)})
    return rows


def main() -> None:
    rows = asyncio.run(_bench())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"docker latency -> {OUT}")
    for r in rows:
        print(f"  {r['pattern']:28s} p50={r['p50_ms']:.2f} p95={r['p95_ms']:.2f} p99={r['p99_ms']:.2f} ms")


if __name__ == "__main__":
    main()
