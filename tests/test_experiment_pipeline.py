"""Experiment harness + aggregator: determinism, calibration hashing, and Holm correctness."""
from __future__ import annotations

import numpy as np
import pandas as pd

from experiments.analyze_results import pairwise_tests, summarize
from experiments.calibration import calibration_sha256, derive_seed, load_calibration
from experiments.metrics import evaluate_trial
from experiments.workload import generate_trial


def _trial(**over):
    cal = load_calibration()
    args = dict(master_seed=20260615, scenario="S2", replicas=5, cache_ratio=0.5,
                failure_inject=0.1, partition="none", trial=0, calibration=cal)
    args.update(over)
    return generate_trial(**args)


def test_workload_is_deterministic_for_same_seed():
    a = _trial()
    b = _trial()
    assert [i.ground_truth for i in a] == [i.ground_truth for i in b]
    assert [tuple(p.status.as_tuple() for p in i.peers) for i in a] == \
           [tuple(p.status.as_tuple() for p in i.peers) for i in b]


def test_workload_changes_with_seed():
    a = _trial(master_seed=20260615)
    b = _trial(master_seed=20260616)
    assert [tuple(p.status.as_tuple() for p in i.peers) for i in a] != \
           [tuple(p.status.as_tuple() for p in i.peers) for i in b]


def test_environment_rng_is_system_independent():
    # derive_seed must NOT include the strategy name -> identical streams across systems.
    s1 = derive_seed(1, "S2", 5, 0.5, 0.1, "none", 0)
    s2 = derive_seed(1, "S2", 5, 0.5, 0.1, "none", 0)
    assert s1 == s2


def test_calibration_hash_is_stable():
    assert calibration_sha256() == calibration_sha256(load_calibration())
    assert len(calibration_sha256()) == 64


def test_centralized_is_correctness_ceiling_and_naive_is_floor():
    instances = _trial(failure_inject=0.0)
    cal = load_calibration()
    central = evaluate_trial("centralized", instances, tau=0.6, replicas=5, local_ms=0.2)
    naive = evaluate_trial("naive-cache", instances, tau=0.6, replicas=5, local_ms=0.2)
    assert central["stale_rate"] == 0.0          # authority always holds the truth
    assert naive["stale_rate"] > central["stale_rate"]


def test_holm_pvalues_dominate_raw():
    # Synthetic per-trial frame: neutro-waa clearly less stale than naive-cache.
    rng = np.random.default_rng(0)
    rows = []
    for system, base in [("neutro-waa", 0.1), ("naive-cache", 0.5), ("quorum-bool", 0.3)]:
        for phi in (0.0, 0.1):
            for seed in (1, 2):
                for trial in range(30):
                    rows.append({
                        "scenario": "S2", "system": system, "failure_inject_phi": phi,
                        "partition": "none", "random_seed": seed, "trial": trial,
                        "stale_rate": float(np.clip(base + rng.normal(0, 0.02), 0, 1)),
                    })
    df = pd.DataFrame(rows)
    out = pairwise_tests(df, "stale_rate", "F1_stale",
                         ["neutro-waa", "naive-cache", "quorum-bool"])
    assert not out.empty
    assert (out["p_holm"] >= out["p_raw"] - 1e-12).all()   # Holm never decreases a p-value


def test_summarize_emits_ci_bounds():
    df = pd.DataFrame({
        "scenario": ["S2"] * 6, "system": ["neutro-waa"] * 6,
        "failure_inject_phi": [0.1] * 6, "partition": ["none"] * 6,
        "trial": range(6), "stale_rate": [0.2, 0.25, 0.22, 0.18, 0.24, 0.21],
        "availability": [1.0] * 6, "failure_rate": [0.0] * 6,
        "messages_mean": [5] * 6, "mlat_p50": [2.0] * 6, "mlat_p99": [5.0] * 6,
        "i_occupancy": [0.4] * 6, "neutro_bool_disagree": [0.5] * 6, "status": ["provisional"] * 6,
    })
    out = summarize(df, {"bootstrap_resamples": 1000, "failure_rate_gate": 0.05})
    assert len(out) == 1
    row = out.iloc[0]
    assert row.stale_ci_lo <= row.stale_rate <= row.stale_ci_hi
