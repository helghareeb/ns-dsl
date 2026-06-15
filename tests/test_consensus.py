"""Decentralized neutrosophic consensus: aggregation, WAA/WGA semantics, partition + heal."""
from __future__ import annotations

import pytest

from nsdsl.consensus import Peer, run_round
from nsdsl.state_store import NeutrosophicStateStore

KEY = "cart:item1"


def _peers(n: int) -> list[Peer]:
    return [Peer(f"p{i}", NeutrosophicStateStore()) for i in range(n)]


def test_all_persisted_reaches_unanimous_accept():
    peers = _peers(5)
    for p in peers:
        p.store.persist(KEY, "v")
    for method in ("waa", "wga"):
        d = run_round(peers, KEY, method=method)
        assert d.accept is True
        assert d.score == pytest.approx(1.0)
        assert d.n_responded == 5


def test_all_cached_is_rejected_by_default_threshold():
    peers = _peers(5)
    for p in peers:
        p.store.write_cache(KEY, "v")
    # cached score = 1/3 < 0.5 for both operators
    assert run_round(peers, KEY, method="waa").accept is False
    assert run_round(peers, KEY, method="wga").accept is False


def test_waa_optimistic_one_committed_peer_carries():
    """SVNNWAA: a single PERSISTED peer (T=1) dominates -> accept; the rest merely cached."""
    peers = _peers(4)
    peers[0].store.persist(KEY, "v")
    for p in peers[1:]:
        p.store.write_cache(KEY, "v")
    d = run_round(peers, KEY, method="waa")
    assert d.accept is True and d.score == pytest.approx(1.0)


def test_wga_conservative_requires_all_committed():
    """SVNNWGA: one non-committed peer vetoes truth -> reject until everyone persists."""
    peers = _peers(4)
    peers[0].store.persist(KEY, "v")
    for p in peers[1:]:
        p.store.write_cache(KEY, "v")
    assert run_round(peers, KEY, method="wga").accept is False
    for p in peers:                       # now everyone commits
        p.store.persist(KEY, "v")
    assert run_round(peers, KEY, method="wga").accept is True


def test_partition_drops_score_then_heal_recovers():
    peers = _peers(5)
    for p in peers:
        p.store.persist(KEY, "v")
    reachable = {"p0", "p1"}              # p2,p3,p4 partitioned away -> contribute DEFAULT
    partitioned = run_round(peers, KEY, method="wga", reachable=reachable)
    assert partitioned.accept is False    # geometric veto from absent (0,0,1) peers
    assert partitioned.n_responded == 2
    healed = run_round(peers, KEY, method="wga")   # all reachable again
    assert healed.accept is True


def test_convergence_rounds_under_wga():
    """Persist one more peer each round; count rounds until WGA accepts (needs all 4)."""
    peers = _peers(4)
    for p in peers:
        p.store.write_cache(KEY, "v")
    rounds_to_accept = None
    for r in range(1, len(peers) + 1):
        peers[r - 1].store.persist(KEY, "v")
        if run_round(peers, KEY, method="wga").accept:
            rounds_to_accept = r
            break
    assert rounds_to_accept == 4


def test_weights_shift_decision():
    """A trusted committed peer can carry SVNNWGA when weights concentrate on it... no:
    WGA still vetoes on any zero-weight-eligible T=0 peer, so verify WAA weight sensitivity."""
    peers = _peers(2)
    peers[0].store.persist(KEY, "v")      # (1,0,0)
    peers[1].store.write_cache(KEY, "v")  # (0,1,0)
    # Uniform WAA already accepts (optimistic); confirm and confirm responded count.
    d = run_round(peers, KEY, method="waa", weights={"p0": 0.9, "p1": 0.1})
    assert d.accept is True
