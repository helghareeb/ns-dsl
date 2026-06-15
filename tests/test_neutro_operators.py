"""SVNNWAA / SVNNWGA aggregation operators: worked example, properties, conservative semantics."""
from __future__ import annotations

from functools import reduce

import pytest
from hypothesis import given
from hypothesis import strategies as st

from nsdsl.neutro import SVNN, normalize_weights, svnnwaa, svnnwga
from nsdsl.neutro.states import DEFAULT, PERSISTED

# Hand-computed worked example (two SVNNs, equal weights). Verified analytically:
#   z1=(0.5,0.3,0.2), z2=(0.7,0.1,0.4), w=[0.5,0.5]
#   SVNNWAA: T=1-sqrt(0.5*0.3), I=sqrt(0.3*0.1), F=sqrt(0.2*0.4)
#   SVNNWGA: T=sqrt(0.5*0.7),   I=1-sqrt(0.7*0.9), F=1-sqrt(0.8*0.6)
Z1 = SVNN(0.5, 0.3, 0.2)
Z2 = SVNN(0.7, 0.1, 0.4)
W = [0.5, 0.5]


def test_svnnwaa_worked_example():
    r = svnnwaa([Z1, Z2], W)
    assert r.almost_equal(SVNN(0.6127016654, 0.1732050808, 0.2828427125), tol=1e-9)


def test_svnnwga_worked_example():
    r = svnnwga([Z1, Z2], W)
    # T=sqrt(0.35), I=1-sqrt(0.63), F=1-sqrt(0.48)
    assert r.almost_equal(SVNN(0.5916079783, 0.2062746067, 0.3071796770), tol=1e-9)


def test_closed_form_matches_algebra_fold():
    """SVNNWAA == oplus-fold of scaled terms; SVNNWGA == otimes-fold of powered terms."""
    zs = [SVNN(0.4, 0.2, 0.1), SVNN(0.6, 0.3, 0.2), SVNN(0.5, 0.5, 0.3)]
    w = normalize_weights([0.2, 0.3, 0.5], 3)
    waa_fold = reduce(lambda a, b: a.oplus(b), (z.scale(wj) for z, wj in zip(zs, w)))
    wga_fold = reduce(lambda a, b: a.otimes(b), (z.power(wj) for z, wj in zip(zs, w)))
    assert svnnwaa(zs, w).almost_equal(waa_fold, tol=1e-9)
    assert svnnwga(zs, w).almost_equal(wga_fold, tol=1e-9)


@given(
    t=st.floats(0, 1), i=st.floats(0, 1), f=st.floats(0, 1),
    ws=st.lists(st.floats(0.01, 10.0), min_size=1, max_size=8),
)
def test_idempotence(t, i, f, ws):
    """Aggregating n copies of the same SVNN returns it, for any weights (both operators)."""
    z = SVNN(t, i, f)
    zs = [z] * len(ws)
    assert svnnwaa(zs, ws).almost_equal(z, tol=1e-9)
    assert svnnwga(zs, ws).almost_equal(z, tol=1e-9)


@given(
    zs=st.lists(
        st.builds(SVNN, st.floats(0, 1), st.floats(0, 1), st.floats(0, 1)),
        min_size=1, max_size=8,
    ),
)
def test_waa_truth_dominates_wga_truth(zs):
    """Arithmetic mean of truth >= geometric mean of truth (AM-GM)."""
    assert svnnwaa(zs).T >= svnnwga(zs).T - 1e-12


def test_svnnwga_conservative_veto_on_zero_truth():
    """One peer certain the value is not committed (T=0) collapses geometric-aggregate truth."""
    zs = [PERSISTED, PERSISTED, SVNN(0.0, 0.5, 0.5)]
    assert svnnwga(zs).T == pytest.approx(0.0)
    # arithmetic averaging does not veto -- it still credits the persisting peers.
    assert svnnwaa(zs).T > 0.0


def test_all_default_aggregates_to_default():
    assert svnnwaa([DEFAULT] * 4).almost_equal(DEFAULT)
    assert svnnwga([DEFAULT] * 4).almost_equal(DEFAULT)


def test_weight_validation():
    with pytest.raises(ValueError):
        svnnwaa([Z1, Z2], [0.5, 0.5, 0.5])   # wrong length
    with pytest.raises(ValueError):
        svnnwaa([Z1, Z2], [-1.0, 2.0])        # negative
    with pytest.raises(ValueError):
        svnnwaa([])                            # empty
