"""Aggregate peer views into a crisp accept/reject decision -- the core contribution.

Pipeline (chapter section 2.8.3.4, decentralized): collect each peer's SVNN view -> weight ->
aggregate with SVNNWAA or SVNNWGA -> deneutrosophize (score) -> accept iff score >= tau. No
central authority participates. SVNNWAA is optimistic (a single committed peer can carry the
decision); SVNNWGA is conservative (a single uncommitted/absent peer vetoes), which is why the
two operators are compared as an ablation (RQ5).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from ..neutro import SVNN, score
from ..neutro.operators import aggregate as aggregate_op

#: An operator-panel member name (see ``nsdsl.neutro.operators.OPERATORS``): "waa"/"wga" are the
#: submitted optimistic/conservative pair; the rest are the Axis-A panel.
Method = str


@dataclass(frozen=True, slots=True)
class ConsensusDecision:
    key: str
    method: Method
    aggregate: SVNN
    score: float
    accept: bool
    n_peers: int
    n_responded: int


def aggregate_views(
    views: Mapping[str, SVNN],
    *,
    method: Method = "waa",
    weights: Mapping[str, float] | None = None,
    tau: float = 0.5,
    key: str = "",
    n_responded: int | None = None,
) -> ConsensusDecision:
    if not views:
        raise ValueError("aggregate_views requires at least one peer view")
    peer_ids = list(views)
    zs = [views[p] for p in peer_ids]
    w = [weights[p] for p in peer_ids] if weights is not None else None
    agg = aggregate_op(method, zs, w)
    s = score(agg)
    return ConsensusDecision(
        key=key,
        method=method,
        aggregate=agg,
        score=s,
        accept=s >= tau,
        n_peers=len(peer_ids),
        n_responded=len(peer_ids) if n_responded is None else n_responded,
    )
