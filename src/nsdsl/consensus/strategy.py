"""Our neutrosophic decision strategies, exposed under the unified read-decision interface.

The (T,I,F) aggregate gates whether to act: SVNNWAA is optimistic (acts as soon as the cluster's
aggregate confidence clears tau -- e.g. a confirmed peer carries it), SVNNWGA is conservative
(acts only on broad confirmation). When it acts, it serves the value confirmed by the persisted
peers (falling back to cached holders), so a single confidently-stale peer does not silently win
a majority.
"""
from __future__ import annotations

from typing import Sequence

from ..baselines.base import DecisionParams, PeerReply, Reading, pick_value
from ..neutro import DEFAULT, PERSISTED
from .aggregate import Method, aggregate_views


def _decide(replies: Sequence[PeerReply], p: DecisionParams, method: Method) -> Reading:
    # Unreachable peers contribute DEFAULT = (0,0,1): "not seen" reads as falsity.
    views = {r.peer_id: (r.status if r.reachable else DEFAULT) for r in replies}
    if not views:
        return Reading(False)
    decision = aggregate_views(views, method=method, weights=p.weights, tau=p.tau)
    if not decision.accept:
        return Reading(False)
    persisted = [r for r in replies if r.reachable and r.status == PERSISTED]
    cached = [r for r in replies if r.reachable and r.status is not DEFAULT]
    return pick_value(persisted or cached)


def neutro_waa(replies: Sequence[PeerReply], p: DecisionParams) -> Reading:
    return _decide(replies, p, "waa")


def neutro_wga(replies: Sequence[PeerReply], p: DecisionParams) -> Reading:
    return _decide(replies, p, "wga")
