"""Axis-B metaheuristic weight/tau tuning (G3): the panel runs offline, beats uniform, is reproducible."""
from __future__ import annotations

import numpy as np

from experiments.calibration import load_calibration
from experiments.tune_weights import OPTIMIZERS, make_fitness, tune

CAL = load_calibration()
R = CAL["tier_a"]["replicas"]


def test_panel_has_seven_optimizers_no_manual():
    assert set(OPTIMIZERS) == {"random", "de", "cmaes", "tpe", "pso", "rime", "nioa"}


def test_objective_returns_finite_float():
    obj = make_fitness("neutro-waa-g", "S1", CAL, reps=1, n_seeds=1)
    val = obj(np.array([0.5] + [1.0] * R))
    assert isinstance(val, float) and np.isfinite(val)


def test_tune_returns_valid_rows_for_every_optimizer():
    df = tune("neutro-waa-g", "S1", budget=8, seed=20260615, cal=CAL, reps=1, n_seeds=1)
    assert set(df["optimizer"]) == set(OPTIMIZERS)
    tau_lo, tau_hi = min(CAL["tau_grid"]), max(CAL["tau_grid"])
    assert (df["tau"].between(tau_lo - 1e-9, tau_hi + 1e-9)).all()
    assert (df["n_evals"] > 0).all()


def test_tuned_utility_beats_uniform_weights():
    df = tune("neutro-waa-g", "S1", budget=10, seed=20260615, cal=CAL, reps=2, n_seeds=1)
    obj = make_fitness("neutro-waa-g", "S1", CAL, reps=2, n_seeds=1)
    uniform = -obj(np.array([0.5] + [1.0] * R))
    assert df["utility"].max() >= uniform - 1e-9


def test_pure_numpy_optimizers_are_deterministic():
    for opt in ("rime", "nioa", "random"):
        a = tune("neutro-waa-g", "S1", budget=8, seed=7, cal=CAL, reps=1, n_seeds=1)
        b = tune("neutro-waa-g", "S1", budget=8, seed=7, cal=CAL, reps=1, n_seeds=1)
        ua = a[a.optimizer == opt]["utility"].iloc[0]
        ub = b[b.optimizer == opt]["utility"].iloc[0]
        assert ua == ub
