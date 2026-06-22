"""Axis-B: tune [tau, peer-weights] with an equal-budget metaheuristic panel.

The submitted layer uses a hand-fit tau and uniform peer weights. This tunes the full vector
[tau, w_0..w_{R-1}] against the same held-out calibration utility (availability minus a
per-scenario cost on the stale-decision rate), comparing optimizers reused from the sibling
edge-dq-ai panel -- random, DE, CMA-ES, TPE, PSO, RIME, NiOA -- at an IDENTICAL evaluation budget.
Because the objective is the fast cached calibration sim, every optimizer is cheap. It answers the
No-Free-Lunch question (Wolpert & Macready 1997; Sorensen 2015): once the budget is fixed, does the
optimizer choice matter? Output: results/tables/weight_tuning.csv. Analysis tool, not a grid system.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from nsdsl.optim.base import run_optimizer
from nsdsl.optim.library import LIBRARY_OPTIMIZERS
from nsdsl.optim.nioa import nioa
from nsdsl.optim.rime import rime

from .calibration import load_calibration
from .metrics import evaluate_trial
from .workload import generate_trial

#: Equal-budget optimizer panel (random is the honest floor; NiOA is provisional, see its module).
OPTIMIZERS = {**LIBRARY_OPTIMIZERS, "rime": rime, "nioa": nioa}

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables" / "weight_tuning.csv"


def make_fitness(system: str, scenario: str, cal: dict, *, reps: int | None = None,
                 n_seeds: int | None = None):
    """Build the minimisation objective f([tau, w_0..w_{R-1}]) = -utility, on held-out seeds.

    reps / n_seeds reduce the calibration budget for a faster optimizer comparison (the full
    fit uses cal['calibration_reps'] and every calibration seed)."""
    R = cal["tier_a"]["replicas"]
    rho = cal["tier_a"]["cache_ratio"]
    local = cal["latency_model_ms"]["local"]
    cost = cal["stale_cost"][scenario]
    reps = cal["calibration_reps"] if reps is None else reps
    seeds = cal["calibration_seeds"][: n_seeds] if n_seeds else cal["calibration_seeds"]

    def objective(x) -> float:
        tau = float(x[0])
        weights = {f"p{i}": float(x[1 + i]) for i in range(R)}
        vals: list[float] = []
        for seed in seeds:
            for phi in cal["tier_a"]["failure_inject"]:
                for partition in cal["tier_a"]["partition"]:
                    for trial in range(reps):
                        inst = generate_trial(
                            master_seed=seed, scenario=scenario, replicas=R, cache_ratio=rho,
                            failure_inject=phi, partition=partition, trial=trial, calibration=cal)
                        m = evaluate_trial(system, inst, tau=tau, replicas=R,
                                           local_ms=local, weights=weights)
                        vals.append(m["availability"] - cost * m["stale_rate"])
        return -(sum(vals) / len(vals))   # minimise -> maximise utility

    return objective


def tune(system: str = "neutro-waa-g", scenario: str = "S1", *, budget: int = 120,
         seed: int = 20260615, cal: dict | None = None, reps: int | None = None,
         n_seeds: int | None = None) -> pd.DataFrame:
    """Run the equal-budget panel; return best utility/tau per optimizer, descending by utility."""
    cal = cal or load_calibration()
    R = cal["tier_a"]["replicas"]
    tau_lo, tau_hi = min(cal["tau_grid"]), max(cal["tau_grid"])
    bounds = np.array([[tau_lo, tau_hi]] + [[0.0, 1.0]] * R)
    obj = make_fitness(system, scenario, cal, reps=reps, n_seeds=n_seeds)
    rows = []
    for name, opt_fn in OPTIMIZERS.items():
        res = run_optimizer(name, opt_fn, obj, bounds, budget, seed)
        rows.append({
            "system": system, "scenario": scenario, "optimizer": name,
            "utility": round(-res.best_f, 4), "tau": round(float(res.best_x[0]), 4),
            "n_evals": res.n_evals, "wall_s": round(res.wall_clock, 2),
        })
    return pd.DataFrame(rows).sort_values("utility", ascending=False).reset_index(drop=True)


def main() -> None:
    cal = load_calibration()
    frames = [tune(scenario=sc, cal=cal) for sc in cal["scenarios"]]
    df = pd.concat(frames, ignore_index=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(df.to_string(index=False))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
