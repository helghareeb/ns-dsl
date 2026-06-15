"""Unified read-decision model so every strategy is scored on equal footing.

A client wants the current value of a key. Each peer reports a ``PeerReply`` (the value it
holds, its neutrosophic status, a logical version for LWW merging, and whether it responds this
round). A strategy consumes the replies and returns a ``Reading``: either it *acts* on a value
(scored for staleness against the oracle) or it *abstains* (scored for unavailability). This
acted-vs-abstain framing is what makes the correctness/availability trade-off (the Pareto story)
measurable and fair across our neutrosophic layer and all baselines.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from ..neutro import SVNN


@dataclass(frozen=True, slots=True)
class PeerReply:
    peer_id: str
    value: Any            # value the peer currently holds (None if never seen)
    status: SVNN          # PERSISTED / CACHED / DEFAULT
    version: int          # logical version of the held value (0 if unseen) -- for LWW merge
    reachable: bool       # does the peer respond this round (failure/partition injection)


@dataclass(frozen=True, slots=True)
class Reading:
    acted: bool           # did the strategy commit to a value?
    value: Any = None     # the value acted on (meaningful only when acted)


@dataclass(frozen=True, slots=True)
class DecisionParams:
    tau: float = 0.5
    decider_id: str = "p0"      # the local node for naive-cache
    authority_id: str = "p0"    # the central authority for centralized
    leader_id: str = "p0"       # the leader for raft-lww
    pick_index: int = 0         # deterministic peer choice for single-peer (set by seeded workload)
    weights: Mapping[str, float] | None = None


Strategy = Callable[[Sequence[PeerReply], DecisionParams], Reading]


def by_id(replies: Sequence[PeerReply], peer_id: str) -> PeerReply | None:
    for r in replies:
        if r.peer_id == peer_id:
            return r
    return None


def pick_value(replies: Sequence[PeerReply]) -> Reading:
    """Majority value among ``replies``; ties broken toward the highest-version holder."""
    pool = [r for r in replies if r.value is not None]
    if not pool:
        return Reading(False)
    counts = Counter(r.value for r in pool)
    top = max(counts.values())
    candidates = {v for v, c in counts.items() if c == top}
    if len(candidates) == 1:
        return Reading(True, next(iter(candidates)))
    best = max((r for r in pool if r.value in candidates), key=lambda r: r.version)
    return Reading(True, best.value)
