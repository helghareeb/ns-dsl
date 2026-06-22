"""Scalability sweep: vary the number of replicas R and report stale-rate, availability, and the
mean per-decision message cost, to show how the decision layer's correctness/availability trade-off
and its communication overhead scale with cluster size.

Held at S2, phi=0.1, no partition, rho=0.5, across all master seeds, with the frozen per-system tau.
Output: results/tables/scalability.csv.
"""
from __future__ import annotations

import csv
from pathlib import Path

from .calibration import load_calibration
from .metrics import evaluate_trial
from .workload import generate_trial

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables" / "scalability.csv"
TAU_FIT = ROOT / "results" / "tables" / "tau_fit.csv"

SCENARIO = "S2"
PHI = 0.1
PARTITION = "none"
RHO = 0.5
SYSTEMS = ["neutro-waa-g", "neutro-median-g", "quorum-bool", "lww-crdt", "centralized"]
R_LEVELS = [2, 3, 5, 7, 10, 20, 50]


def _tau_fit() -> dict[tuple[str, str], float]:
    if not TAU_FIT.exists():
        return {}
    with TAU_FIT.open() as fh:
        return {(r["scenario"], r["system"]): float(r["tau"]) for r in csv.DictReader(fh)}


def _point(cal, tau_fit, system, R):
    """Mean stale-rate, availability, and messages/decision for one (system, R) over all seeds x reps."""
    tau = tau_fit.get((SCENARIO, system), cal["scenarios"][SCENARIO]["tau"])
    local = cal["latency_model_ms"]["local"]
    stale, avail, msgs, n = 0.0, 0.0, 0.0, 0
    for seed in cal["random_seeds"]:
        for trial in range(cal["reps_per_cell"]):
            inst = generate_trial(master_seed=seed, scenario=SCENARIO, replicas=R, cache_ratio=RHO,
                                  failure_inject=PHI, partition=PARTITION, trial=trial,
                                  calibration=cal)
            m = evaluate_trial(system, inst, tau=tau, replicas=R, local_ms=local)
            stale += m["stale_rate"]
            avail += m["availability"]
            msgs += m["messages_mean"]
            n += 1
    return stale / n, avail / n, msgs / n


def main() -> None:
    cal = load_calibration()
    tau_fit = _tau_fit()
    rows = []
    for system in SYSTEMS:
        for R in R_LEVELS:
            s, a, msg = _point(cal, tau_fit, system, R)
            rows.append({"replicas": R, "system": system, "stale_rate": round(s, 4),
                         "availability": round(a, 4), "messages_mean": round(msg, 2)})
        print(f"[scalability] {system}: done", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["replicas", "system", "stale_rate", "availability", "messages_mean"])
        w.writeheader()
        w.writerows(rows)
    print(f"scalability -> {OUT} ({len(rows)} points)")


if __name__ == "__main__":
    main()
