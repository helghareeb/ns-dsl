"""Standalone peer ASGI app for the Dockerized testbed.

Each container runs this app; it serves a peer's neutrosophic view for a key over HTTP. The
in-process latency benchmark (``bench/latency_bench.py``) builds the same app for measurement;
this module is the container entrypoint (``uvicorn bench.peer_server:app``).
"""
from __future__ import annotations

import asyncio
import os
import random

from fastapi import FastAPI

PEER_ID = os.environ.get("PEER_ID", "p0")
DEFAULT_RTT_MS = float(os.environ.get("RTT_MS", "2.0"))
JITTER_FRAC = 0.25

app = FastAPI(title=f"ns-dsl peer {PEER_ID}")
_rng = random.Random(hash(PEER_ID) & 0xFFFFFFFF)


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "peer": PEER_ID}


@app.get("/view/{pid}")
async def view(pid: str, rtt: float = DEFAULT_RTT_MS) -> dict:
    await asyncio.sleep(max(0.0, _rng.gauss(rtt, rtt * JITTER_FRAC)) / 1000.0)
    return {"peer": pid, "T": 1.0, "I": 0.0, "F": 0.0, "value": "v", "version": 1}
