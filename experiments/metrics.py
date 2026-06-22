"""Evaluate a strategy over one trial's decision stream and compute per-trial metrics.

Correctness (stale-rate) is computed over decisions the strategy ACTED on (success-only, Rule
R8); availability is the fraction that produced a decision at all. Simulated latency uses an
analytical network model (clearly labelled; real wall-clock latency comes from the Docker
testbed) with the wait pattern of each strategy: one hop, k-th-of-majority, or all reachable.
"""
from __future__ import annotations

from statistics import quantiles
from typing import Sequence

from nsdsl.baselines import STRATEGIES, DecisionParams
from nsdsl.neutro.states import DEFAULT

from .workload import AUTHORITY_ID, DECIDER_ID, DecisionInstance

_ONE_HOP = {"single-peer", "centralized", "raft-lww"}
_ALL_HOPS = {"neutro-waa", "neutro-wga", "lww-crdt"}
_MAJORITY = {"quorum-bool", "pbs-quorum"}


def messages_per_decision(system: str, replicas: int) -> int:
    if system in {"neutro-waa", "neutro-wga", "quorum-bool", "lww-crdt"}:
        return replicas
    if system == "pbs-quorum":
        return replicas // 2 + 1            # partial quorum
    if system == "naive-cache":
        return 0
    return 1


def _params(system: str, inst: DecisionInstance, tau: float,
            weights: dict[str, float] | None = None):
    return DecisionParams(
        tau=tau, decider_id=DECIDER_ID, authority_id=AUTHORITY_ID,
        leader_id=AUTHORITY_ID, pick_index=inst.pick_index, weights=weights,
    )


def _replies(system: str, inst: DecisionInstance):
    if system in {"centralized", "raft-lww"}:
        return [inst.authority]
    return list(inst.peers)


def _latency(system: str, inst: DecisionInstance, local_ms: float) -> float:
    if system == "naive-cache":
        return local_ms
    if system in {"centralized", "raft-lww"}:
        return local_ms + inst.auth_hop_ms
    reachable_hops = [h for p, h in zip(inst.peers, inst.hops_ms)
                      if p.reachable and p.status is not DEFAULT]
    if not reachable_hops:
        return local_ms
    if system == "single-peer":
        return local_ms + reachable_hops[inst.pick_index % len(reachable_hops)]
    if system in _MAJORITY:
        k = len(reachable_hops) // 2          # k-th fastest gives a majority once it returns
        return local_ms + sorted(reachable_hops)[k]
    return local_ms + max(reachable_hops)      # ALL_HOPS: wait for every reachable peer


def evaluate_trial(system: str, instances: Sequence[DecisionInstance], *,
                   tau: float, replicas: int, local_ms: float,
                   weights: dict[str, float] | None = None) -> dict:
    n = len(instances)
    n_acted = n_stale = 0
    latencies: list[float] = []
    for inst in instances:
        reading = STRATEGIES[system](_replies(system, inst), _params(system, inst, tau, weights))
        if not reading.acted:
            continue
        n_acted += 1
        if reading.value != inst.ground_truth:
            n_stale += 1
        latencies.append(_latency(system, inst, local_ms))

    stale_rate = n_stale / n_acted if n_acted else 0.0
    availability = n_acted / n if n else 0.0
    p50, p95, p99 = _percentiles(latencies)
    return {
        "system": system,
        "n_decisions": n,
        "n_acted": n_acted,
        "n_stale": n_stale,
        "stale_rate": stale_rate,
        "availability": availability,
        "failure_rate": 1.0 - availability,
        "messages_mean": messages_per_decision(system, replicas),
        "mlat_p50": p50,
        "mlat_p95": p95,
        "mlat_p99": p99,
        "i_occupancy": sum(i.i_occupancy for i in instances) / n if n else 0.0,
    }


def neutro_bool_disagreement(instances: Sequence[DecisionInstance], *, tau: float) -> float:
    """RQ1: fraction of decisions where neutro-waa and quorum-bool disagree on the same inputs.

    Quantifies the decisions the (T,I,F) signal exposes that a boolean fresh/stale flag collapses.
    """
    if not instances:
        return 0.0
    diff = 0
    for inst in instances:
        replies = list(inst.peers)
        a = STRATEGIES["neutro-waa"](replies, _params("neutro-waa", inst, tau))
        b = STRATEGIES["quorum-bool"](replies, _params("quorum-bool", inst, tau))
        if (a.acted, a.value) != (b.acted, b.value):
            diff += 1
    return diff / len(instances)


def _percentiles(values: list[float]) -> tuple[float, float, float]:
    if not values:
        return (float("nan"),) * 3
    if len(values) < 2:
        v = values[0]
        return (v, v, v)
    cuts = quantiles(values, n=100, method="inclusive")  # cuts[i] ~ (i+1)-th percentile
    return (cuts[49], cuts[94], cuts[98])
