"""Our neutrosophic decision strategies, exposed under the unified read-decision interface.

The (T,I,F) aggregate gates whether to act: SVNNWAA is optimistic (acts as soon as the cluster's
aggregate confidence clears tau -- e.g. a confirmed peer carries it), SVNNWGA is conservative
(acts only on broad confirmation). When it acts, it serves the value confirmed by the persisted
peers (falling back to cached holders), so a single confidently-stale peer does not silently win
a majority.

Two enrichments live here behind the same interface:
  * the Axis-A operator panel (``method`` is any ``nsdsl.neutro.operators.OPERATORS`` member), and
  * the encoding mode: "crisp" (submitted; peers report SVNN corners) or "graded" (peers' views are
    softened by their observable version lag, so the operator panel differentiates -- see
    ``nsdsl.neutro.encode``). The VALUE served is unchanged; only the act/abstain gate sees the
    graded views.
"""
from __future__ import annotations

from typing import Mapping, Sequence

from ..baselines.base import DecisionParams, PeerReply, Reading, pick_value
from ..neutro import DEFAULT, PERSISTED, SVNN
from ..neutro.encode import grade, grade_views
from ..neutro.operators import OPERATORS
from .aggregate import Method, aggregate_views


def _build_views(replies: Sequence[PeerReply], encoding: str) -> Mapping[str, SVNN]:
    if encoding == "graded":
        reachable = [r for r in replies if r.reachable]
        graded = grade_views([r.status for r in reachable], [r.version for r in reachable])
        views: dict[str, SVNN] = {r.peer_id: g for r, g in zip(reachable, graded)}
        absent = grade(DEFAULT, 0)
        for r in replies:
            if not r.reachable:
                views[r.peer_id] = absent
        return views
    # crisp (submitted): unreachable peers contribute DEFAULT = (0,0,1).
    return {r.peer_id: (r.status if r.reachable else DEFAULT) for r in replies}


def _decide(replies: Sequence[PeerReply], p: DecisionParams, method: Method,
            *, encoding: str = "crisp") -> Reading:
    views = _build_views(replies, encoding)
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


def make_neutro_strategy(method: Method, encoding: str = "graded"):
    """Build a read-decision strategy for an operator-panel member under an encoding mode."""
    def strat(replies: Sequence[PeerReply], p: DecisionParams) -> Reading:
        return _decide(replies, p, method, encoding=encoding)
    strat.__name__ = f"neutro_{method}_{encoding}"
    return strat


#: Axis-A operator panel under the graded encoding (where the operators differentiate). The
#: submitted crisp ``neutro-waa``/``neutro-wga`` remain registered separately and unchanged.
GRADED_STRATEGIES = {
    f"neutro-{op}-g": make_neutro_strategy(op, "graded") for op in OPERATORS
}
