"""Seeded workload model: generate the per-decision peer-reply sets and ground truth.

For each decision the harness advances a ground-truth value and samples each peer's local view
of it. A peer either holds the latest value (PERSISTED if it has confirmed it, CACHED if only
in cache -- the I axis, populated in proportion to cache_ratio rho), holds an older value
(stale; confidently so when PERSISTED), or has never seen it (DEFAULT). Reachability injects
failures (rate phi) and partitions. Crucially the RNG is seeded WITHOUT the strategy name, so
every strategy is scored on the identical decision stream (a paired design, Rule R5).
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from math import exp

from nsdsl.baselines.base import PeerReply
from nsdsl.neutro.states import CACHED, DEFAULT, PERSISTED

from .calibration import derive_seed

DECIDER_ID = "p0"
AUTHORITY_ID = "auth"


@dataclass(frozen=True, slots=True)
class DecisionInstance:
    peers: tuple[PeerReply, ...]        # ordinary decentralized peers
    authority: PeerReply               # strong primary (centralized / raft leader)
    ground_truth: str
    pick_index: int                    # deterministic single-peer choice
    hops_ms: tuple[float, ...]         # per-ordinary-peer simulated network latency
    auth_hop_ms: float
    i_occupancy: float                 # mean indeterminacy across peers (RQ1 signal richness)


def _lognormal(rng: random.Random, mu: float, sigma: float) -> float:
    return exp(rng.gauss(mu_to_log(mu), sigma))


def mu_to_log(mean_ms: float) -> float:
    # interpret hop_mu in the calibration as the median (geometric mean) in ms
    from math import log
    return log(mean_ms)


def _sample_peer(rng: random.Random, pid: str, gt: str, version: int, scn: dict,
                 rho: float) -> PeerReply:
    has_latest = rng.random() < scn["base_has_latest"]
    if has_latest:
        if rng.random() < rho:                                       # in cache only (unconfirmed)
            if rng.random() < scn["dirty_cache_prob"]:
                # dirty read: a later uncommitted write sits in cache (highest version) but will
                # never become the committed truth -- reading it yields a wrong value.
                return PeerReply(pid, f"{gt}_dirty", CACHED, version + 1, True)
            return PeerReply(pid, gt, CACHED, version, True)         # clean cache: holds the truth
        return PeerReply(pid, gt, PERSISTED, version, True)          # latest, confirmed
    if rng.random() < scn["stale_vs_unseen"]:
        old = f"v{version - 1}"
        status = PERSISTED if rng.random() < scn["stale_persist_frac"] else CACHED
        return PeerReply(pid, old, status, version - 1, True)        # stale (confidently if PERSISTED)
    return PeerReply(pid, None, DEFAULT, 0, True)                    # never seen


def _apply_reachability(rng: random.Random, peers: list[PeerReply], auth: PeerReply,
                        phi: float, partitioned: bool) -> tuple[list[PeerReply], PeerReply]:
    out: list[PeerReply] = []
    split = (len(peers) + 1) // 2
    for idx, p in enumerate(peers):
        reachable = rng.random() >= phi
        if partitioned and idx >= split:        # peers on the far side of the split
            reachable = False
        out.append(PeerReply(p.peer_id, p.value, p.status, p.version, reachable))
    auth_reachable = rng.random() >= phi and not partitioned   # auth sits across the split
    auth = PeerReply(auth.peer_id, auth.value, auth.status, auth.version, auth_reachable)
    return out, auth


def generate_trial(
    *, master_seed: int, scenario: str, replicas: int, cache_ratio: float,
    failure_inject: float, partition: str, trial: int, calibration: dict,
) -> list[DecisionInstance]:
    """Generate one trial's decision stream. Identical across strategies (system excluded)."""
    seed = derive_seed(master_seed, scenario, replicas, cache_ratio, failure_inject,
                       partition, trial)
    rng = random.Random(seed)
    scn = calibration["scenarios"][scenario]
    lat = calibration["latency_model_ms"]
    n_decisions = calibration["decisions_per_trial"]
    partition_prob = calibration["partition_prob"]

    instances: list[DecisionInstance] = []
    for n in range(1, n_decisions + 1):
        gt = f"v{n}"
        peers = [_sample_peer(rng, f"p{i}", gt, n, scn, cache_ratio) for i in range(replicas)]
        authority = PeerReply(AUTHORITY_ID, gt, PERSISTED, n, True)
        partitioned = partition == "transient" and rng.random() < partition_prob
        peers, authority = _apply_reachability(rng, peers, authority, failure_inject, partitioned)

        hops = tuple(_lognormal(rng, lat["hop_mu"], lat["hop_sigma"]) for _ in peers)
        auth_hop = _lognormal(rng, lat["hop_mu"], lat["hop_sigma"])
        i_occ = sum(p.status.I for p in peers) / len(peers)
        instances.append(DecisionInstance(
            peers=tuple(peers), authority=authority, ground_truth=gt,
            pick_index=rng.randrange(replicas), hops_ms=hops, auth_hop_ms=auth_hop,
            i_occupancy=i_occ,
        ))
    return instances
