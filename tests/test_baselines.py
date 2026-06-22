"""Read-decision strategies: per-strategy behavior and the honest comparisons."""
from __future__ import annotations

from nsdsl.baselines import STRATEGIES, DecisionParams, PeerReply
from nsdsl.neutro.states import CACHED, DEFAULT, PERSISTED

LATEST = "v2"
OLD = "v1"


def reply(pid, value, status, version=2, reachable=True):
    return PeerReply(pid, value, status, version, reachable)


def run(name, replies, **kw):
    return STRATEGIES[name](replies, DecisionParams(**kw))


def test_registry_has_all_strategies():
    from nsdsl.consensus.strategy import GRADED_STRATEGIES
    base = {
        "neutro-waa", "neutro-wga", "centralized", "quorum-bool", "pbs-quorum",
        "raft-lww", "lww-crdt", "single-peer", "naive-cache",
    }
    assert set(STRATEGIES) == base | set(GRADED_STRATEGIES)
    # the graded Axis-A operator panel is registered (G1)
    assert {"neutro-einstein-g", "neutro-dombi-g", "neutro-bonferroni-g"} <= set(STRATEGIES)


def test_pbs_quorum_reads_partial_quorum_latest():
    # PBS acts (never abstains when peers reachable) and returns the latest among its quorum.
    replies = [reply("p0", OLD, CACHED, version=1), reply("p1", LATEST, PERSISTED, version=3),
               reply("p2", OLD, CACHED, version=1)]
    r = run("pbs-quorum", replies, pick_index=0)
    assert r.acted is True
    assert r.value in {OLD, LATEST}        # depends on which majority-quorum it sampled


def test_all_persisted_latest_everyone_acts_correctly():
    replies = [reply(f"p{i}", LATEST, PERSISTED) for i in range(5)]
    for name in STRATEGIES:
        r = run(name, replies)
        assert r.acted and r.value == LATEST, name


def test_one_persisted_rest_cached_waa_acts_quorum_abstains():
    # p0 has confirmed the latest; p1..p4 hold it only in cache.
    replies = [reply("p0", LATEST, PERSISTED)] + [
        reply(f"p{i}", LATEST, CACHED) for i in range(1, 5)
    ]
    # WAA is optimistic: one confirmation carries the decision -> acts on the confirmed value.
    waa = run("neutro-waa", replies)
    assert waa.acted and waa.value == LATEST
    # quorum-of-booleans needs a MAJORITY confirmed -> cannot act (the cost of collapsing T,I,F).
    assert run("quorum-bool", replies).acted is False
    # WGA is conservative: not broadly confirmed -> abstains.
    assert run("neutro-wga", replies).acted is False


def test_centralized_stalls_when_authority_unreachable():
    replies = [reply("p0", LATEST, PERSISTED, reachable=False)] + [
        reply(f"p{i}", LATEST, PERSISTED) for i in range(1, 4)
    ]
    assert run("centralized", replies, authority_id="p0").acted is False
    assert run("centralized", replies, authority_id="p1").value == LATEST


def test_raft_unavailable_without_leader():
    replies = [reply("p0", LATEST, PERSISTED, reachable=False),
               reply("p1", LATEST, PERSISTED)]
    assert run("raft-lww", replies, leader_id="p0").acted is False
    assert run("raft-lww", replies, leader_id="p1").acted is True


def test_neutro_wga_vetoes_under_partition_waa_survives():
    # All hold the latest, but p2,p3,p4 are partitioned away -> contribute DEFAULT.
    replies = [reply("p0", LATEST, PERSISTED), reply("p1", LATEST, PERSISTED)] + [
        reply(f"p{i}", LATEST, PERSISTED, reachable=False) for i in range(2, 5)
    ]
    assert run("neutro-wga", replies).acted is False     # geometric veto from absent peers
    assert run("neutro-waa", replies).value == LATEST    # a reachable confirmation carries it


def test_lww_and_naive_can_read_stale():
    # Latest (v2, version 3) lives only on an unreachable peer; reachable peers have old v1.
    replies = [
        reply("p0", OLD, CACHED, version=1),
        reply("p1", OLD, CACHED, version=1),
        reply("p2", LATEST, PERSISTED, version=3, reachable=False),
    ]
    assert run("lww-crdt", replies).value == OLD          # eventually consistent -> stale read
    assert run("naive-cache", replies, decider_id="p0").value == OLD


def test_single_peer_uses_deterministic_pick_index():
    replies = [reply("p0", OLD, CACHED), reply("p1", LATEST, PERSISTED)]
    assert run("single-peer", replies, pick_index=0).value == OLD
    assert run("single-peer", replies, pick_index=1).value == LATEST


def test_all_remote_unreachable_only_local_naive_cache_acts():
    # "reachable" governs response to *remote* queries; the local node still reads its own cache.
    replies = [reply(f"p{i}", LATEST, PERSISTED, reachable=False) for i in range(5)]
    for name in STRATEGIES:
        if name == "naive-cache":
            assert run(name, replies, decider_id="p0").acted is True  # local read, always available
        else:
            assert run(name, replies).acted is False, name
