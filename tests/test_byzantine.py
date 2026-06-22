"""Byzantine faults + robust aggregation (G4).

Robust aggregators defend the act/abstain GATE: a minority of confidence-inflating adversarial
triples cannot drag the aggregate confidence, so the layer abstains instead of acting on poisoned
evidence. (Majority value-selection is a separate vector, discussed in the manuscript.)
"""
from __future__ import annotations

from nsdsl.baselines import DecisionParams, PeerReply, STRATEGIES
from nsdsl.neutro import operators as OP
from nsdsl.neutro.score import score
from nsdsl.neutro.states import CACHED, DEFAULT, PERSISTED
from nsdsl.neutro.svnn import SVNN

from experiments.calibration import load_calibration
from experiments.workload import generate_trial

CAL = load_calibration()


# --- aggregation-level robustness (the real guarantee) -----------------------

def test_robust_operators_resist_a_single_inflated_outlier():
    honest = [SVNN(0.2, 0.6, 0.1)] * 4
    outlier = SVNN(1.0, 0.0, 0.0)              # adversary claims fully-true
    zs = honest + [outlier]
    waa_T = OP.svnnwaa(zs).T
    for name in ("median", "trimmed", "krum"):
        z = OP.aggregate(name, zs)
        assert z.T <= waa_T                    # robust truth is not dragged up by the outlier
        assert z.T < 0.6                       # stays near the honest cluster, not near 1


def test_krum_selects_an_honest_cluster_member():
    honest = [SVNN(0.30, 0.50, 0.20), SVNN(0.32, 0.48, 0.20), SVNN(0.31, 0.49, 0.20)]
    outliers = [SVNN(1.0, 0.0, 0.0), SVNN(0.0, 0.0, 1.0)]
    z = OP.svnn_krum(honest + outliers, f=2)
    assert z.T < 0.5 and z.I > 0.3             # a member of the honest cluster, not an outlier


def test_robust_operators_are_valid_and_idempotent():
    z = SVNN(0.4, 0.3, 0.3)
    for name in ("median", "trimmed", "krum"):
        r = OP.aggregate(name, [z, z, z])
        assert r.almost_equal(z, tol=1e-9)


def test_robust_operators_registered_in_panel_and_as_strategies():
    assert {"median", "trimmed", "krum"} <= set(OP.OPERATORS)
    assert {"neutro-median-g", "neutro-trimmed-g", "neutro-krum-g"} <= set(STRATEGIES)


# --- Byzantine fault model ---------------------------------------------------

def _trial(byz):
    return generate_trial(master_seed=20260615, scenario="S2", replicas=5, cache_ratio=0.5,
                          failure_inject=0.1, partition="none", trial=0, calibration=CAL,
                          byzantine_frac=byz)


def test_byzantine_zero_is_a_noop_regression():
    """byzantine_frac=0 consumes no RNG, so the decision stream is byte-identical to the baseline."""
    a = _trial(0.0)
    b = generate_trial(master_seed=20260615, scenario="S2", replicas=5, cache_ratio=0.5,
                       failure_inject=0.1, partition="none", trial=0, calibration=CAL)
    assert [p.peers for p in a] == [p.peers for p in b]


def test_byzantine_injects_adversaries():
    insts = _trial(0.4)
    n_byz = sum(1 for inst in insts for p in inst.peers
                if isinstance(p.value, str) and p.value.endswith("_byz"))
    assert n_byz > 0                           # adversaries present
    # an adversary claims PERSISTED at an inflated version
    advs = [p for inst in insts for p in inst.peers
            if isinstance(p.value, str) and p.value.endswith("_byz")]
    assert all(p.status == PERSISTED for p in advs)


def test_gate_robustness_on_a_confidence_inflating_minority():
    """One Byzantine PERSISTED peer amid uncertain (cached) honest peers fools the optimistic WAA
    gate into acting, while the robust median keeps the aggregate score lower (resists the lone
    inflated triple)."""
    from nsdsl.consensus.strategy import _build_views
    from nsdsl.consensus.aggregate import aggregate_views
    rs = [
        PeerReply("p0", "v3_byz", PERSISTED, 5, True),   # adversary: inflated confidence + version
        PeerReply("p1", "v3", CACHED, 3, True),
        PeerReply("p2", "v3", CACHED, 3, True),
        PeerReply("p3", "v3", CACHED, 3, True),
        PeerReply("p4", "v3", CACHED, 3, True),
    ]
    views = _build_views(rs, "graded")
    waa_score = aggregate_views(views, method="waa").score
    median_score = aggregate_views(views, method="median").score
    assert median_score < waa_score            # robust gate is less inflated by the adversary
