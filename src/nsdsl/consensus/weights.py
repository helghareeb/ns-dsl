"""Peer weighting strategies for aggregation. Weights are normalized downstream."""
from __future__ import annotations

import math
from collections.abc import Iterable, Mapping


def uniform(peer_ids: Iterable[str]) -> dict[str, float]:
    return {pid: 1.0 for pid in peer_ids}


def from_trust(trust: Mapping[str, float], peer_ids: Iterable[str]) -> dict[str, float]:
    """Weight each peer by a configured trust/reliability score (default 1.0)."""
    return {pid: float(trust.get(pid, 1.0)) for pid in peer_ids}


def from_staleness(staleness: Mapping[str, float], peer_ids: Iterable[str],
                   half_life: float = 1.0) -> dict[str, float]:
    """Weight fresher views higher: w = 0.5 ** (staleness / half_life), decaying with age."""
    return {pid: 0.5 ** (float(staleness.get(pid, 0.0)) / half_life) for pid in peer_ids}
