"""SVNN type + algebra: validation, complement, and the per-term building blocks."""
from __future__ import annotations

import math

import pytest

from nsdsl.neutro import SVNN
from nsdsl.neutro.states import CACHED, DEFAULT, PERSISTED, parse_status


def test_components_must_be_in_unit_interval():
    SVNN(0.0, 0.0, 0.0)
    SVNN(1.0, 1.0, 1.0)
    with pytest.raises(ValueError):
        SVNN(1.5, 0.0, 0.0)
    with pytest.raises(ValueError):
        SVNN(0.0, -0.1, 0.0)


def test_complement():
    z = SVNN(0.7, 0.2, 0.1)
    assert z.complement().almost_equal(SVNN(0.1, 0.8, 0.7))


def test_canonical_states_and_typo_fix():
    assert PERSISTED.as_tuple() == (1.0, 0.0, 0.0)
    assert CACHED.as_tuple() == (0.0, 1.0, 0.0)
    # ERRATUM fix: default is (0,0,1), NOT the chapter's printed (0,1,0).
    assert DEFAULT.as_tuple() == (0.0, 0.0, 1.0)
    assert DEFAULT != CACHED


def test_parse_status_roundtrips_canonical_states():
    assert parse_status("(1,0,0)") is PERSISTED
    assert parse_status("(0,1,0)") is CACHED
    assert parse_status(" (0, 0, 1) ") is DEFAULT
    arbitrary = parse_status("(0.5,0.3,0.2)")
    assert arbitrary.almost_equal(SVNN(0.5, 0.3, 0.2))


def test_scale_and_power_are_complementary_building_blocks():
    z = SVNN(0.5, 0.3, 0.2)
    # scale (per-term of SVNNWAA): w*z = (1-(1-T)^w, I^w, F^w)
    s = z.scale(0.5)
    assert math.isclose(s.T, 1.0 - (0.5 ** 0.5))
    assert math.isclose(s.I, 0.3 ** 0.5)
    # power (per-term of SVNNWGA): z^w = (T^w, 1-(1-I)^w, 1-(1-F)^w)
    p = z.power(0.5)
    assert math.isclose(p.T, 0.5 ** 0.5)
    assert math.isclose(p.I, 1.0 - (0.7 ** 0.5))


def test_negative_weights_rejected():
    z = SVNN(0.5, 0.3, 0.2)
    with pytest.raises(ValueError):
        z.scale(-1.0)
    with pytest.raises(ValueError):
        z.power(-1.0)
