"""Deneutrosophy score and the accept decision."""
from __future__ import annotations

import pytest

from nsdsl.neutro import SVNN, decide, score
from nsdsl.neutro.states import CACHED, DEFAULT, PERSISTED


def test_score_of_canonical_states():
    assert score(PERSISTED) == pytest.approx(1.0)      # (2+1-0-0)/3
    assert score(CACHED) == pytest.approx(1.0 / 3.0)   # (2+0-1-0)/3
    assert score(DEFAULT) == pytest.approx(1.0 / 3.0)  # (2+0-0-1)/3


def test_score_is_monotone_in_truth():
    assert score(SVNN(0.9, 0.1, 0.0)) > score(SVNN(0.4, 0.1, 0.0))


def test_score_in_unit_interval_for_extremes():
    assert score(SVNN(0.0, 1.0, 1.0)) == pytest.approx(0.0)
    assert score(SVNN(1.0, 0.0, 0.0)) == pytest.approx(1.0)


def test_decide_threshold():
    assert decide(PERSISTED, threshold=0.5) is True
    assert decide(CACHED, threshold=0.5) is False      # 0.333 < 0.5
    assert decide(CACHED, threshold=0.3) is True


# === Deneutrosophy score panel (Axis A') =====================================

from hypothesis import given  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

from nsdsl.neutro.score import SCORES  # noqa: E402


def test_default_score_fn_is_standard():
    z = SVNN(0.6, 0.3, 0.2)
    assert score(z) == pytest.approx(score(z, "standard"))
    assert score(z, "standard") == pytest.approx(SCORES["standard"](z))


@given(t=st.floats(0, 1), i=st.floats(0, 1), f=st.floats(0, 1))
def test_every_score_in_unit_interval(t, i, f):
    z = SVNN(t, i, f)
    for name in SCORES:
        s = score(z, name)
        assert 0.0 <= s <= 1.0


def test_all_scores_peak_at_truth_corner():
    for name in SCORES:
        assert score(PERSISTED, name) == pytest.approx(1.0)


def test_accuracy_ignores_indeterminacy():
    assert score(SVNN(0.6, 0.1, 0.2), "accuracy") == pytest.approx(
        score(SVNN(0.6, 0.9, 0.2), "accuracy"))


def test_truth_weighted_is_stricter_than_standard_on_cached():
    # a low-truth, high-indeterminacy view scores lower under the truth-dominant score
    z = SVNN(0.3, 0.6, 0.1)
    assert score(z, "truth_weighted") < score(z, "standard")


def test_cosine_matches_truth_direction():
    assert score(SVNN(0.0, 0.5, 0.5), "cosine") == pytest.approx(0.0)
    assert score(SVNN(1.0, 0.0, 0.0), "cosine") == pytest.approx(1.0)


def test_unknown_score_raises():
    with pytest.raises(ValueError):
        score(PERSISTED, "no_such_score")
