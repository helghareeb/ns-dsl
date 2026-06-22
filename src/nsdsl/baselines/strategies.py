"""Baseline read-decision strategies (the comparison set for FGCS reviewers).

Roles in the comparison:
  centralized   -- single strongly-consistent authority: correctness ceiling, stalls on partition
  raft_lww      -- leader holds the replicated committed value: strong-consistency reference
  quorum_bool   -- majority vote over BOOLEAN fresh/stale flags: the apples-to-apples control
                   that isolates the value of (T,I,F) versus a single bit
  lww_crdt      -- last-writer-wins register, eventually consistent: latency floor, reads can be stale
  single_peer   -- ask one reachable peer: the chapter's implicit baseline
  naive_cache   -- act on the local cache, no coordination: correctness/latency floor
"""
from __future__ import annotations

from typing import Sequence

from ..neutro.states import DEFAULT, PERSISTED
from .base import DecisionParams, PeerReply, Reading, by_id, pick_value


def centralized(replies: Sequence[PeerReply], p: DecisionParams) -> Reading:
    authority = by_id(replies, p.authority_id)
    if authority is None or not authority.reachable or authority.status is DEFAULT:
        return Reading(False)        # unavailable when the authority is unreachable
    return Reading(True, authority.value)


def raft_lww(replies: Sequence[PeerReply], p: DecisionParams) -> Reading:
    leader = by_id(replies, p.leader_id)
    if leader is None or not leader.reachable or leader.status is DEFAULT:
        return Reading(False)        # no leader this round -> unavailable (models re-election gap)
    return Reading(True, leader.value)


def quorum_bool(replies: Sequence[PeerReply], p: DecisionParams) -> Reading:
    responding = [r for r in replies if r.reachable]
    if not responding:
        return Reading(False)
    fresh = [r for r in responding if r.status == PERSISTED]
    if len(fresh) * 2 <= len(responding):   # no strict majority of confirmed-fresh peers
        return Reading(False)               # the boolean flag cannot confirm -> abstain
    return pick_value(fresh)


def lww_crdt(replies: Sequence[PeerReply], p: DecisionParams) -> Reading:
    pool = [r for r in replies if r.reachable and r.status is not DEFAULT]
    if not pool:
        return Reading(False)
    best = max(pool, key=lambda r: r.version)
    return Reading(True, best.value)        # eventually consistent: may be stale


def single_peer(replies: Sequence[PeerReply], p: DecisionParams) -> Reading:
    reachable = [r for r in replies if r.reachable and r.status is not DEFAULT]
    if not reachable:
        return Reading(False)
    chosen = reachable[p.pick_index % len(reachable)]
    return Reading(True, chosen.value)


def naive_cache(replies: Sequence[PeerReply], p: DecisionParams) -> Reading:
    local = by_id(replies, p.decider_id)
    if local is None:
        return Reading(False)
    return Reading(True, local.value)       # acts on its own copy regardless of freshness


def freshness_slo(replies: Sequence[PeerReply], p: DecisionParams) -> Reading:
    """Adaptive-freshness reader (RALF/Pileus-inspired, as a decentralized per-read dual).

    Acts iff the latest value the cluster has is CONFIRMED-committed: some reachable peer reports
    PERSISTED at the maximum reachable version (a 'confirmed-latest' freshness SLO). Otherwise the
    latest is only cached/unconfirmed and it abstains. This sits between quorum-bool (which needs a
    majority of persisted) and lww-crdt (which serves the freshest value confirmed or not), and --
    unlike our layer -- it collapses the (T,I,F) signal to a single confirmed-latest bit.
    """
    reachable = [r for r in replies if r.reachable and r.status is not DEFAULT]
    if not reachable:
        return Reading(False)
    max_v = max(r.version for r in reachable)
    confirmed_latest = [r for r in reachable if r.version == max_v and r.status == PERSISTED]
    if not confirmed_latest:
        return Reading(False)              # latest is unconfirmed -> freshness SLO not met
    return pick_value(confirmed_latest)


def pbs_quorum(replies: Sequence[PeerReply], p: DecisionParams) -> Reading:
    """Probabilistically-bounded-staleness style partial-quorum read (Bailis et al.).

    Reads a partial quorum (majority-sized) of the reachable peers and returns the highest-version
    value among them, always acting (bounded, not zero, staleness) -- the nearest prior art. It is
    cheaper than reading all peers (lww-crdt) but staler than a full read; unlike quorum-bool it
    does not abstain, and unlike our layer it ignores the (T,I,F) confirmation signal.
    """
    reachable = [r for r in replies if r.reachable and r.status is not DEFAULT]
    if not reachable:
        return Reading(False)
    k = len(replies) // 2 + 1                       # target partial-quorum size
    ordered = sorted(reachable, key=lambda r: r.peer_id)
    start = p.pick_index % len(ordered)             # deterministic quorum selection
    quorum = (ordered + ordered)[start:start + k]   # k peers, wrapping
    best = max(quorum, key=lambda r: r.version)
    return Reading(True, best.value)
