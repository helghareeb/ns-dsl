"""Ground-truth oracle: god-log + state reconstruction."""
from __future__ import annotations

from nsdsl.oracle import GodLog, Oracle


def test_true_value_is_last_commit_at_or_before_time():
    log = GodLog()
    log.append("cart:item1", "v1")     # seq 1
    log.append("cart:item1", "v2")     # seq 2
    log.append("cart:item2", "x")      # seq 3
    oracle = Oracle(log)
    assert oracle.true_value("cart:item1", at=1) == "v1"
    assert oracle.true_value("cart:item1", at=2) == "v2"
    assert oracle.true_value("cart:item1") == "v2"        # latest
    assert oracle.true_value("cart:item2", at=2) is None  # not yet committed at seq 2


def test_global_state_snapshot():
    log = GodLog()
    log.append("a", 1)
    log.append("b", 2)
    log.append("a", 3)
    oracle = Oracle(log)
    assert oracle.global_state(at=2) == {"a": 1, "b": 2}
    assert oracle.global_state() == {"a": 3, "b": 2}


def test_is_stale():
    log = GodLog()
    log.append("k", "fresh")
    oracle = Oracle(log)
    assert oracle.is_stale("k", "old") is True
    assert oracle.is_stale("k", "fresh") is False
