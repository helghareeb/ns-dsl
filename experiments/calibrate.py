"""Fit the acceptance threshold tau per (scenario, neutrosophic system) on HELD-OUT calibration seeds.

Internal-validity guard: tau is chosen on calibration_seeds (disjoint from the evaluation
random_seeds) by maximizing a stated utility -- availability minus a per-scenario cost on the
stale-decision rate -- then frozen before evaluation. Every neutrosophic strategy that uses the
score>=tau gate is fitted (the submitted crisp pair, the Axis-A graded operator panel, and the
Axis-A' score panel); the non-neutro baselines ignore tau. The calibration decision streams are
system-independent, so each is generated ONCE per scenario cell and reused across all systems and
tau values. Output: results/tables/tau_fit.csv.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from nsdsl.baselines import STRATEGIES

from .calibration import load_calibration
from .metrics import evaluate_trial
from .workload import generate_trial

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables" / "tau_fit.csv"

#: Every strategy that consumes the score>=tau gate (the submitted crisp pair + the Axis-A graded
#: operator/robust panel + the Axis-A' score panel). The non-neutro baselines ignore tau.
NEUTRO_SYSTEMS = [name for name in STRATEGIES if name.startswith("neutro-")]


def _calibration_trials(scenario: str, cal: dict) -> list:
    """Generate the held-out calibration decision streams once (independent of the system/tau)."""
    R = cal["tier_a"]["replicas"]
    rho = cal["tier_a"]["cache_ratio"]
    reps = cal["calibration_reps"]
    trials = []
    for seed in cal["calibration_seeds"]:
        for phi in cal["tier_a"]["failure_inject"]:
            for partition in cal["tier_a"]["partition"]:
                for trial in range(reps):
                    trials.append(generate_trial(
                        master_seed=seed, scenario=scenario, replicas=R, cache_ratio=rho,
                        failure_inject=phi, partition=partition, trial=trial, calibration=cal))
    return trials


def _utility(system: str, scenario: str, tau: float, trials: list, cal: dict) -> float:
    R = cal["tier_a"]["replicas"]
    local = cal["latency_model_ms"]["local"]
    cost = cal["stale_cost"][scenario]
    vals = [
        (m["availability"] - cost * m["stale_rate"])
        for inst in trials
        for m in (evaluate_trial(system, inst, tau=tau, replicas=R, local_ms=local),)
    ]
    return sum(vals) / len(vals)


def fit(cal: dict | None = None, systems: list[str] | None = None) -> pd.DataFrame:
    cal = cal or load_calibration()
    systems = systems or NEUTRO_SYSTEMS
    rows = []
    for scenario in cal["scenarios"]:
        trials = _calibration_trials(scenario, cal)          # generate ONCE per scenario
        for system in systems:
            scored = [(tau, _utility(system, scenario, tau, trials, cal)) for tau in cal["tau_grid"]]
            best_tau, best_u = max(scored, key=lambda t: t[1])
            rows.append({"scenario": scenario, "system": system,
                         "tau": best_tau, "utility": round(best_u, 4)})
        print(f"[calibrate] scenario={scenario}: fitted tau for {len(systems)} systems", flush=True)
    return pd.DataFrame(rows)


def main() -> None:
    df = fit()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(df.to_string(index=False))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
