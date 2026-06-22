"""Measured decision latency on a REAL localhost HTTP testbed.

Unlike the analytical latency model in the simulation, this stands up a real ASGI server (uvicorn)
serving one endpoint per peer and drives it with a real async HTTP client (httpx). Each strategy
executes its TRUE communication pattern over real sockets -- one hop (centralized / raft / single),
wait-for-majority (quorum), or wait-for-all + real SVNN aggregation (neutro / lww) -- and we time
wall-clock decision latency end to end. A configurable per-hop RTT (server-side async delay) models
network distance; all serialization, socket, scheduling, and aggregation costs are real and measured.

Run:  PYTHONPATH=src:. python -m bench.latency_bench
"""
from __future__ import annotations

import asyncio
import contextlib
import csv
import random
import threading
import time
from pathlib import Path
from statistics import quantiles

import httpx
import uvicorn
from fastapi import FastAPI

from nsdsl.neutro import SVNN, svnnwaa, svnnwga

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables" / "latency_measured.csv"
HOST, PORT = "127.0.0.1", 8731
BASE = f"http://{HOST}:{PORT}"
REPLICAS = 5
N_DECISIONS = 200
RTT_LEVELS_MS = [1.0, 5.0, 20.0]
JITTER_FRAC = 0.25

from nsdsl.consensus.strategy import GRADED_STRATEGIES  # noqa: E402

ONE_HOP = {"single-peer", "centralized", "raft-lww"}
# The graded operator panel fans out to every peer, like the crisp neutro strategies.
ALL_HOPS = {"neutro-waa", "neutro-wga", "lww-crdt", *GRADED_STRATEGIES}
MAJORITY = {"quorum-bool", "pbs-quorum"}
LOCAL = {"naive-cache"}


def build_app() -> FastAPI:
    app = FastAPI()
    rng = random.Random(20260615)

    @app.get("/health")
    async def health() -> dict:
        return {"ok": True}

    @app.get("/view/{pid}")
    async def view(pid: str, rtt: float = 2.0) -> dict:
        delay = max(0.0, rng.gauss(rtt, rtt * JITTER_FRAC)) / 1000.0
        await asyncio.sleep(delay)                          # real async per-hop network delay
        return {"peer": pid, "T": 1.0, "I": 0.0, "F": 0.0, "value": "v", "version": 1}

    return app


class _Server:
    def __init__(self, app: FastAPI) -> None:
        self._server = uvicorn.Server(uvicorn.Config(app, host=HOST, port=PORT, log_level="error"))
        self._thread = threading.Thread(target=self._server.run, daemon=True)

    def __enter__(self) -> "_Server":
        self._thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self._server.should_exit = True
        self._thread.join(timeout=5)


async def _wait_ready(client: httpx.AsyncClient) -> None:
    for _ in range(200):
        with contextlib.suppress(Exception):
            if (await client.get(f"{BASE}/health")).status_code == 200:
                return
        await asyncio.sleep(0.05)
    raise RuntimeError("uvicorn did not come up")


async def _one_hop(client: httpx.AsyncClient, rtt: float) -> None:
    await client.get(f"{BASE}/view/auth", params={"rtt": rtt})


async def _all_hops(client: httpx.AsyncClient, rtt: float, system: str) -> None:
    rs = await asyncio.gather(*[client.get(f"{BASE}/view/p{i}", params={"rtt": rtt})
                                for i in range(REPLICAS)])
    payloads = [r.json() for r in rs]
    zs = [SVNN(p["T"], p["I"], p["F"]) for p in payloads]
    if system == "neutro-waa":
        svnnwaa(zs)                                          # real aggregation cost
    elif system == "neutro-wga":
        svnnwga(zs)
    else:  # lww-crdt: pick max version
        max(payloads, key=lambda p: p["version"])


async def _majority(client: httpx.AsyncClient, rtt: float) -> None:
    tasks = [asyncio.create_task(client.get(f"{BASE}/view/p{i}", params={"rtt": rtt}))
             for i in range(REPLICAS)]
    need, done = REPLICAS // 2 + 1, 0
    for fut in asyncio.as_completed(tasks):
        await fut
        done += 1
        if done >= need:
            break
    for t in tasks:
        if not t.done():
            t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


async def _decide(client: httpx.AsyncClient, system: str, rtt: float) -> None:
    if system in LOCAL:
        svnnwaa([SVNN(0.0, 1.0, 0.0)])                       # local-only: tiny real compute
    elif system in ONE_HOP:
        await _one_hop(client, rtt)
    elif system in MAJORITY:
        await _majority(client, rtt)
    else:
        await _all_hops(client, rtt, system)


async def _bench() -> list[dict]:
    rows = []
    systems = sorted({*ONE_HOP, *ALL_HOPS, *MAJORITY, *LOCAL})
    async with httpx.AsyncClient(timeout=10.0) as client:
        await _wait_ready(client)
        for rtt in RTT_LEVELS_MS:
            samples: dict[str, list[float]] = {s: [] for s in systems}
            for _ in range(20):                              # warmup (discarded)
                for system in systems:
                    await _decide(client, system, rtt)
            for _ in range(N_DECISIONS):                     # interleave systems per decision
                for system in systems:                       # to cancel out drift/warmup bias
                    t0 = time.perf_counter()
                    await _decide(client, system, rtt)
                    samples[system].append((time.perf_counter() - t0) * 1000.0)
            for system in systems:
                cuts = quantiles(samples[system], n=100, method="inclusive")
                rows.append({
                    "rtt_ms": rtt, "system": system, "n": N_DECISIONS,
                    "p50_ms": round(cuts[49], 4), "p95_ms": round(cuts[94], 4),
                    "p99_ms": round(cuts[98], 4),
                    "mean_ms": round(sum(samples[system]) / N_DECISIONS, 4),
                })
    return rows


def main() -> None:
    with _Server(build_app()):
        rows = asyncio.run(_bench())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"measured latency -> {OUT} ({len(rows)} rows)")
    for r in rows:
        if r["rtt_ms"] == 5.0:
            print(f"  rtt=5ms {r['system']:12s} p50={r['p50_ms']:.2f} p95={r['p95_ms']:.2f} "
                  f"p99={r['p99_ms']:.2f} ms")


if __name__ == "__main__":
    main()
