"""S3 clone catch-up: a fresh replica replays the logs-as-DSL stream to consensus-consistent state."""
from __future__ import annotations

from nsdsl.consensus import Peer, run_round
from nsdsl.consensus.replay import apply_event, item_key, replay
from nsdsl.neutro.states import DEFAULT, PERSISTED
from nsdsl.state_store import NeutrosophicStateStore

# An ordered stream of DSL event logs (book persisted, then chapter persisted later).
EVENTS = [
    """{"guid":"order1","cartItems":[{"book":"Microservices and DSLs","status":"(1,0,0)"}],"nodeID":"1"}""",
    """{"guid":"order1","cartItems":[{"chapter":"Enterprise Integration","status":"(0,1,0)"}],"nodeID":"1"}""",
    """{"guid":"order1","cartItems":[{"chapter":"Enterprise Integration","status":"(1,0,0)"}],"nodeID":"1"}""",
]


def test_fresh_replica_starts_in_default():
    store = NeutrosophicStateStore()
    assert store.status(item_key("order1", "book")) is DEFAULT


def test_replay_recovers_state():
    store = NeutrosophicStateStore()
    result = replay(store, EVENTS)
    assert result.events_replayed == 3
    assert result.keys_recovered == 2          # book + chapter
    # last event persists chapter -> both items end PERSISTED
    assert store.status(item_key("order1", "book")) is PERSISTED
    assert store.status(item_key("order1", "chapter")) is PERSISTED


def test_cache_then_persist_transition():
    store = NeutrosophicStateStore()
    apply_event(store, EVENTS[1])              # chapter cached
    assert store.get(item_key("order1", "chapter")).status.I == 1.0   # CACHED
    apply_event(store, EVENTS[2])              # chapter persisted
    assert store.status(item_key("order1", "chapter")) is PERSISTED


def test_caught_up_replica_reaches_consensus_with_peers():
    key = item_key("order1", "book")
    established = [Peer(f"p{i}", NeutrosophicStateStore()) for i in range(3)]
    for p in established:
        for text in EVENTS:
            apply_event(p.store, text)
    # before catch-up: the fresh replica drags WGA consensus down (it reports DEFAULT)
    fresh = Peer("clone", NeutrosophicStateStore())
    peers = [*established, fresh]
    assert run_round(peers, key, method="wga").accept is False
    # after replaying the logs, the clone agrees and consensus is unanimous
    replay(fresh.store, EVENTS)
    assert run_round(peers, key, method="wga").accept is True
