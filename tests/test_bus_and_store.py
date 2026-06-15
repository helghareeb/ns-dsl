"""In-process event bus + neutrosophic state store."""
from __future__ import annotations

import pytest

from nsdsl.bus import InProcessBus, NoResponderError
from nsdsl.neutro.states import CACHED, DEFAULT, PERSISTED
from nsdsl.state_store import NeutrosophicStateStore


def test_pub_sub_delivers_to_all_subscribers():
    bus = InProcessBus()
    received: list[int] = []
    bus.subscribe("t", received.append)
    bus.subscribe("t", lambda m: received.append(m * 10))
    bus.publish("t", 5)
    assert received == [5, 50]


def test_request_reply():
    bus = InProcessBus()
    bus.register_responder("sum", lambda p: p["a"] + p["b"])
    assert bus.request("sum", {"a": 2, "b": 3}) == 5


def test_request_without_responder_raises():
    bus = InProcessBus()
    with pytest.raises(NoResponderError):
        bus.request("missing", None)


def test_duplicate_responder_rejected():
    bus = InProcessBus()
    bus.register_responder("x", lambda p: p)
    with pytest.raises(ValueError):
        bus.register_responder("x", lambda p: p)


def test_store_status_transitions():
    store = NeutrosophicStateStore()
    assert store.status("k") is DEFAULT
    store.write_cache("k", 1)
    assert store.get("k").status is CACHED
    assert store.get("k").value == 1
    assert store.flush("k") is True
    assert store.status("k") is PERSISTED


def test_persist_drops_stale_cache():
    store = NeutrosophicStateStore()
    store.write_cache("k", "old")
    store.persist("k", "new")
    got = store.get("k")
    assert got.status is PERSISTED and got.value == "new"
