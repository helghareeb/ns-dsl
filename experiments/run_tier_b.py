"""Tier-B sensitivity sweeps: vary one workload factor at a time around the Tier-A centre.

Sweeps the number of replicas R and the cache ratio rho (the two factors that affect the
correctness/availability model) at phi=0.1, no partition, S2, across all master seeds, for the
decision-layer systems of interest. Output: results/tables/sensitivity.csv.
"""
from __future__ import annotations

import csv
from pathlib import Path

from nsdsl.baselines import STRATEGIES

from .calibration import load_calibration
from .metrics import evaluate_trial
from .workload import generate_trial

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables" / "sensitivity.csv"
TAU_FIT = ROOT / "results" / "tables" / "tau_fit.csv"

SCENARIO = "S2"
PHI = 0.1
PARTITION = "none"
SYSTEMS = ["neutro-waa", "neutro-wga", "quorum-bool", "lww-crdt", "centralized"]
R_LEVELS = [3, 5, 7]
RHO_LEVELS = [0.2, 0.5, 0.8]


def _tau_fit() -> dict[tuple[str, str], float]:
    if not TAU_FIT.exists():
        return {}
    with TAU_FIT.open() as fh:
        return {(r["scenario"], r["system"]): float(r["tau"]) for r in csv.DictReader(fh)}


def _point(cal, tau_fit, system, R, rho):
    """Mean stale-rate and availability for one (system, R, rho) over all seeds x reps."""
    default_tau = cal["scenarios"][SCENARIO]["tau"]
    tau = tau_fit.get((SCENARIO, system), default_tau)
    local = cal["latency_model_ms"]["local"]
    stale, avail, n = 0.0, 0.0, 0
    for seed in cal["random_seeds"]:
        for trial in range(cal["reps_per_cell"]):
            inst = generate_trial(master_seed=seed, scenario=SCENARIO, replicas=R,
                                  cache_ratio=rho, failure_inject=PHI, partition=PARTITION,
                                  trial=trial, calibration=cal)
            m = evaluate_trial(system, inst, tau=tau, replicas=R, local_ms=local)
            stale += m["stale_rate"]
            avail += m["availability"]
            n += 1
    return stale / n, avail / n


def main() -> None:
    cal = load_calibration()
    tau_fit = _tau_fit()
    rows = []
    for system in SYSTEMS:
        for R in R_LEVELS:                                    # vary R at rho=0.5
            s, a = _point(cal, tau_fit, system, R, 0.5)
            rows.append({"factor": "replicas", "value": R, "system": system,
                         "stale_rate": round(s, 4), "availability": round(a, 4)})
        for rho in RHO_LEVELS:                                # vary rho at R=5
            s, a = _point(cal, tau_fit, system, 5, rho)
            rows.append({"factor": "cache_ratio", "value": rho, "system": system,
                         "stale_rate": round(s, 4), "availability": round(a, 4)})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["factor", "value", "system", "stale_rate", "availability"])
        w.writeheader()
        w.writerows(rows)
    print(f"sensitivity -> {OUT} ({len(rows)} points)")


if __name__ == "__main__":
    main()
