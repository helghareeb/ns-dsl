"""
Equal-budget optimization harness (Axis B of the comparative audit).

Every optimizer tunes the 5 decision thresholds in [0,1]^5 against a shared
governance-cost objective under an IDENTICAL budget of objective evaluations. Each
objective evaluation re-runs the decision engine over a validation set and dominates
per-iteration optimizer overhead, so #evaluations is the fair budget unit.

`BudgetedObjective` counts evaluations, records the best-so-far trajectory, and raises
`BudgetExhausted` at exactly `budget` calls — guaranteeing every optimizer spends the
same budget regardless of its internal loop structure.

Honesty framing (Sörensen 2015; No-Free-Lunch, Wolpert & Macready 1997): the panel
pits each metaphor optimizer against trusted classics at equal budget, with >=30 seeded
restarts and Holm-corrected, bootstrapped comparisons downstream.

Author : Independent Research | License: MIT
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np


class BudgetExhausted(Exception):
    """Raised when the objective has been evaluated `budget` times."""


@dataclass
class OptResult:
    name: str
    best_x: np.ndarray
    best_f: float
    n_evals: int
    wall_clock: float
    history: list           # best-so-far objective value after each evaluation


class BudgetedObjective:
    """Wrap an objective fn(x)->float with a hard evaluation budget + best-so-far history."""

    def __init__(self, fn, budget: int, bounds, seed: int = 0):
        self.fn = fn
        self.budget = int(budget)
        self.bounds = np.asarray(bounds, float)
        self.dim = len(self.bounds)
        self.n = 0
        self.best_f = np.inf
        self.best_x = None
        self.history: list[float] = []
        self.rng = np.random.default_rng(seed)

    def __call__(self, x) -> float:
        if self.n >= self.budget:
            raise BudgetExhausted()
        x = np.clip(np.asarray(x, float), self.bounds[:, 0], self.bounds[:, 1])
        f = float(self.fn(x))
        self.n += 1
        if f < self.best_f:
            self.best_f, self.best_x = f, x.copy()
        self.history.append(self.best_f)
        return f

    def sample(self, m: int | None = None):
        lo, hi = self.bounds[:, 0], self.bounds[:, 1]
        if m is None:
            return lo + (hi - lo) * self.rng.random(self.dim)
        return lo + (hi - lo) * self.rng.random((m, self.dim))


def run_optimizer(name: str, opt_fn, fn, bounds, budget: int, seed: int) -> OptResult:
    """Run one optimizer to exactly `budget` evaluations; return its best-so-far result."""
    obj = BudgetedObjective(fn, budget, bounds, seed)
    t0 = time.perf_counter()
    try:
        opt_fn(obj, np.asarray(bounds, float), budget, seed)
    except BudgetExhausted:
        pass
    except Exception as exc:  # noqa: BLE001 — never let one optimizer abort the panel
        print(f"  [warn] optimizer {name} raised {type(exc).__name__}: {exc}")
    wall = time.perf_counter() - t0
    best_x = obj.best_x if obj.best_x is not None else obj.sample()
    return OptResult(name, best_x, obj.best_f, obj.n, wall, obj.history)
