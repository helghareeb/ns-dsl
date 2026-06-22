"""Byzantine robustness sweep: vary the adversarial-peer fraction and compare the robust
aggregators (coordinate-wise median, trimmed mean, Krum) against the averaging operators and the
boolean/eventual baselines under attack.

Adversaries claim PERSISTED while holding a fabricated value at an inflated version (workload
``byzantine_frac``), the worst case for an optimistic operator and for majority value selection.
Held at S2 (asymmetric-cost scenario), phi=0.1, no partition, R=5, rho=0.5, across all master seeds,
with the frozen per-system tau. Output: results/tables/byzantine.csv.
"""
from __future__ import annotations

import csv
from pathlib import Path

from .calibration import load_calibration
from .metrics import evaluate_trial
from .workload import generate_trial

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables" / "byzantine.csv"
TAU_FIT = ROOT / "results" / "tables" / "tau_fit.csv"

SCENARIO = "S2"
PHI = 0.1
PARTITION = "none"
R = 5
RHO = 0.5
SYSTEMS = [
    "neutro-waa-g", "neutro-wga-g",                       # averaging (non-robust)
    "neutro-median-g", "neutro-trimmed-g", "neutro-krum-g",  # robust aggregators
    "quorum-bool", "lww-crdt",                            # boolean / eventual baselines
]
BYZ_LEVELS = [0.0, 0.1, 0.2, 0.4]


def _tau_fit() -> dict[tuple[str, str], float]:
    if not TAU_FIT.exists():
        return {}
    with TAU_FIT.open() as fh:
        return {(r["scenario"], r["system"]): float(r["tau"]) for r in csv.DictReader(fh)}


def _point(cal, tau_fit, system, byz):
    """Mean stale-rate and availability for one (system, byzantine_frac) over all seeds x reps."""
    tau = tau_fit.get((SCENARIO, system), cal["scenarios"][SCENARIO]["tau"])
    local = cal["latency_model_ms"]["local"]
    stale, avail, n = 0.0, 0.0, 0
    for seed in cal["random_seeds"]:
        for trial in range(cal["reps_per_cell"]):
            inst = generate_trial(master_seed=seed, scenario=SCENARIO, replicas=R, cache_ratio=RHO,
                                  failure_inject=PHI, partition=PARTITION, trial=trial,
                                  calibration=cal, byzantine_frac=byz)
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
        for byz in BYZ_LEVELS:
            s, a = _point(cal, tau_fit, system, byz)
            rows.append({"byzantine_frac": byz, "system": system,
                         "stale_rate": round(s, 4), "availability": round(a, 4)})
        print(f"[byzantine] {system}: done", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["byzantine_frac", "system", "stale_rate", "availability"])
        w.writeheader()
        w.writerows(rows)
    print(f"byzantine -> {OUT} ({len(rows)} points)")


if __name__ == "__main__":
    main()
