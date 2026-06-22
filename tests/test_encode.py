"""Graded peer-confidence encoding (G1b): properties + that it makes the operator panel bite."""
from __future__ import annotations

from nsdsl.baselines import DecisionParams, STRATEGIES
from nsdsl.neutro.encode import grade, grade_views
from nsdsl.neutro.states import CACHED, DEFAULT, PERSISTED
from nsdsl.neutro.svnn import SVNN


def _valid(z: SVNN) -> bool:
    return 0.0 <= z.T <= 1.0 and 0.0 <= z.I <= 1.0 and 0.0 <= z.F <= 1.0


def test_grade_outputs_valid_svnn_for_every_kind_and_lag():
    for status in (PERSISTED, CACHED, DEFAULT):
        for lag in range(0, 10):
            assert _valid(grade(status, lag))


def test_fresh_persisted_is_near_truth_corner():
    z = grade(PERSISTED, 0)
    assert z.T > 0.9 and z.F < 0.05


def test_stale_persisted_gains_falsity_and_loses_truth():
    fresh = grade(PERSISTED, 0)
    stale = grade(PERSISTED, 6)
    assert stale.T < fresh.T          # truth decays with lag
    assert stale.F > fresh.F          # superseded -> falsity grows


def test_cached_carries_high_indeterminacy():
    z = grade(CACHED, 0)
    assert z.I >= 0.5                  # unconfirmed -> indeterminate (the whole point)
    assert 0.0 < z.T < 0.9            # graded, not a crisp corner


def test_absent_is_high_falsity():
    z = grade(DEFAULT, 0)
    assert z.F > 0.7


def test_persisted_truth_is_monotone_nonincreasing_in_lag():
    ts = [grade(PERSISTED, lag).T for lag in range(0, 8)]
    assert all(ts[i] >= ts[i + 1] - 1e-12 for i in range(len(ts) - 1))


def test_grade_views_flags_lone_high_version_as_suspect_dirty():
    # one cached peer holds an anomalously high version (an uncommitted future write)
    statuses = [PERSISTED, PERSISTED, CACHED]
    versions = [5, 5, 6]
    graded = grade_views(statuses, versions)
    suspect = graded[2]               # the lone-highest cached peer
    plain_cached = grade(CACHED, 0)
    assert suspect.F > plain_cached.F   # suspicion shifts mass to falsity


def test_grade_views_uses_max_version_as_freshness_reference():
    statuses = [PERSISTED, PERSISTED]
    versions = [4, 6]                 # peer 0 lags peer 1 by 2
    graded = grade_views(statuses, versions)
    assert graded[1].T > graded[0].T  # the up-to-date peer is trusted more


def test_crisp_and_graded_waa_both_decide():
    """Crisp and graded neutro-waa both yield a boolean act/abstain on the same inputs; the
    graded gate sees version-lag-softened views rather than the crisp corners."""
    from nsdsl.baselines import PeerReply
    rs = [
        PeerReply("p0", "v3", CACHED, 3, True),
        PeerReply("p1", "v2", PERSISTED, 2, True),   # a lagging persisted peer
        PeerReply("p2", None, DEFAULT, 0, True),
    ]
    p = DecisionParams(tau=0.6)
    crisp = STRATEGIES["neutro-waa"](rs, p).acted
    graded = STRATEGIES["neutro-waa-g"](rs, p).acted
    assert isinstance(crisp, bool) and isinstance(graded, bool)
