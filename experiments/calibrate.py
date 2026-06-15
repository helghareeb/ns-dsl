"""Fit the acceptance threshold tau per (scenario, operator) on HELD-OUT calibration seeds.

Internal-validity guard: tau is chosen on calibration_seeds (disjoint from the evaluation
random_seeds) by maximizing a stated utility -- availability minus a per-scenario cost on the
stale-decision rate -- then frozen before evaluation. Only the two neutrosophic operators use
tau; the baselines ignore it. Output: results/tables/tau_fit.csv.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .calibration import load_calibration
from .metrics import evaluate_trial
from .workload import generate_trial

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables" / "tau_fit.csv"
OPERATORS = ["neutro-waa", "neutro-wga"]


def _utility(system: str, scenario: str, tau: float, cal: dict) -> float:
    R = cal["tier_a"]["replicas"]
    rho = cal["tier_a"]["cache_ratio"]
    local = cal["latency_model_ms"]["local"]
    cost = cal["stale_cost"][scenario]
    reps = cal["calibration_reps"]
    vals: list[float] = []
    for seed in cal["calibration_seeds"]:
        for phi in cal["tier_a"]["failure_inject"]:
            for partition in cal["tier_a"]["partition"]:
                for trial in range(reps):
                    inst = generate_trial(master_seed=seed, scenario=scenario, replicas=R,
                                          cache_ratio=rho, failure_inject=phi,
                                          partition=partition, trial=trial, calibration=cal)
                    m = evaluate_trial(system, inst, tau=tau, replicas=R, local_ms=local)
                    vals.append(m["availability"] - cost * m["stale_rate"])
    return sum(vals) / len(vals)


def fit(cal: dict | None = None) -> pd.DataFrame:
    cal = cal or load_calibration()
    rows = []
    for scenario in cal["scenarios"]:
        for system in OPERATORS:
            scored = [(tau, _utility(system, scenario, tau, cal)) for tau in cal["tau_grid"]]
            best_tau, best_u = max(scored, key=lambda t: t[1])
            rows.append({"scenario": scenario, "system": system,
                         "tau": best_tau, "utility": round(best_u, 4)})
    return pd.DataFrame(rows)


def main() -> None:
    df = fit()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(df.to_string(index=False))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
