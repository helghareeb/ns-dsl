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
