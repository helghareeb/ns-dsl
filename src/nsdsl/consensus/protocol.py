"""Run a decentralized consensus round over a set of peers.

Unreachable peers (failed or partitioned away) contribute DEFAULT = (0,0,1) -- "I have not seen
it" reads as falsity, not indeterminacy (the erratum fix matters here). This is what lets
correctness/availability be measured under failure injection without any central coordinator.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from ..neutro import DEFAULT, SVNN
from .aggregate import ConsensusDecision, Method, aggregate_views
from .peer_view import Peer
from .weights import uniform


def collect_views(
    peers: Sequence[Peer], key: str, reachable: Iterable[str] | None = None
) -> tuple[dict[str, SVNN], int]:
    """Gather each peer's SVNN for ``key``; unreachable peers contribute DEFAULT."""
    reachable_set = {p.peer_id for p in peers} if reachable is None else set(reachable)
    views: dict[str, SVNN] = {}
    responded = 0
    for peer in peers:
        if peer.peer_id in reachable_set:
            views[peer.peer_id] = peer.view(key)
            responded += 1
        else:
            views[peer.peer_id] = DEFAULT
    return views, responded


def run_round(
    peers: Sequence[Peer],
    key: str,
    *,
    reachable: Iterable[str] | None = None,
    method: Method = "waa",
    weights: Mapping[str, float] | None = None,
    tau: float = 0.5,
) -> ConsensusDecision:
    """One consensus round: collect -> weight -> aggregate -> deneutrosophize -> decide."""
    views, responded = collect_views(peers, key, reachable)
    if weights is None:
        weights = uniform(views)
    return aggregate_views(
        views, method=method, weights=weights, tau=tau, key=key, n_responded=responded
    )
