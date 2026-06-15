"""Measured throughput (decisions/sec) under closed-loop concurrent load on the real testbed.

Reuses the live HTTP peer server from ``latency_bench``. For each strategy we keep a fixed number
of decisions in flight for a fixed duration and count completions -- so strategies that fan out to
all peers (neutro / lww) sustain fewer decisions/sec than a single-hop authority, and a local read
(naive) is highest. The single-worker server is the shared bottleneck, so numbers are comparative.

Run:  PYTHONPATH=src:. python -m bench.throughput_bench
"""
from __future__ import annotations

import asyncio
import csv
import time
from pathlib import Path

import httpx

from . import latency_bench as lb

OUT = Path(__file__).resolve().parents[1] / "results" / "tables" / "throughput.csv"
RTT_MS = 2.0
DURATION_S = 3.0
CONCURRENCY = 32


async def _worker(client: httpx.AsyncClient, system: str, deadline: float, counter: list[int]) -> None:
    while time.perf_counter() < deadline:
        await lb._decide(client, system, RTT_MS)
        counter[0] += 1


async def _bench() -> list[dict]:
    systems = sorted({*lb.ONE_HOP, *lb.ALL_HOPS, *lb.MAJORITY, *lb.LOCAL})
    rows = []
    limits = httpx.Limits(max_connections=256, max_keepalive_connections=256)
    async with httpx.AsyncClient(timeout=15.0, limits=limits) as client:
        await lb._wait_ready(client)
        for system in systems:
            for _ in range(CONCURRENCY * 2):                 # warmup
                await lb._decide(client, system, RTT_MS)
            counter = [0]
            t0 = time.perf_counter()
            deadline = t0 + DURATION_S
            await asyncio.gather(*[_worker(client, system, deadline, counter)
                                   for _ in range(CONCURRENCY)])
            elapsed = time.perf_counter() - t0
            rows.append({"system": system, "concurrency": CONCURRENCY,
                         "decisions": counter[0], "throughput_dps": round(counter[0] / elapsed, 1)})
    return rows


def main() -> None:
    with lb._Server(lb.build_app()):
        rows = asyncio.run(_bench())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"throughput -> {OUT}")
    for r in sorted(rows, key=lambda x: -x["throughput_dps"]):
        print(f"  {r['system']:12s} {r['throughput_dps']:8.1f} dec/s")


if __name__ == "__main__":
    main()
