"""Experiment harness: sweep the grid, evaluate every strategy on identical decision streams,
and write hash-stamped raw per-trial CSVs (Rule R5/R6). The aggregator turns these into the
canonical summary; this script does no statistics itself.

Usage:
    PYTHONPATH=src:. python experiments/run_all.py            # full Tier-A grid, all seeds
    PYTHONPATH=src:. python experiments/run_all.py --quick    # fast smoke (1 seed, few reps)
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import subprocess
from pathlib import Path

from nsdsl.baselines import STRATEGIES

from .calibration import calibration_sha256, load_calibration
from .metrics import evaluate_trial, neutro_bool_disagreement
from .workload import generate_trial

RAW_DIR = Path(__file__).resolve().parents[1] / "results" / "raw"

COLUMNS = [
    "calibration_sha256", "code_git_sha", "random_seed", "status",
    "scenario", "system", "replicas_R", "cache_ratio_rho", "failure_inject_phi", "partition",
    "trial", "n_decisions", "n_acted", "n_stale", "stale_rate", "availability",
    "failure_rate", "messages_mean", "mlat_p50", "mlat_p95", "mlat_p99",
    "i_occupancy", "neutro_bool_disagree",
]


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _write_header(fh, cal_sha: str, git_sha: str, seed: int, status: str) -> None:
    fh.write(f"# calibration_sha256: {cal_sha}\n")
    fh.write(f"# code_git_sha: {git_sha}\n")
    fh.write(f"# random_seed: {seed}\n")
    fh.write(f"# status: {status}\n")
    fh.write(f"# generated_utc: {dt.datetime.now(dt.timezone.utc).isoformat()}\n")
    fh.write("# schema_version: 1\n")


def run(quick: bool = False) -> list[Path]:
    cal = load_calibration()
    cal_sha = calibration_sha256(cal)
    git_sha = _git_sha()
    status = "provisional"   # tau not yet fit on a held-out workload; promote at M10

    seeds = cal["random_seeds"][:1] if quick else cal["random_seeds"]
    reps = 5 if quick else cal["reps_per_cell"]
    decisions = 40 if quick else cal["decisions_per_trial"]
    cal = {**cal, "decisions_per_trial": decisions}

    tier_a = cal["tier_a"]
    R = tier_a["replicas"]
    rho = tier_a["cache_ratio"]
    local_ms = cal["latency_model_ms"]["local"]
    scenarios = list(cal["scenarios"])
    systems = list(STRATEGIES)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for seed in seeds:
        path = RAW_DIR / f"raw_seed{seed}{'_quick' if quick else ''}.csv"
        with path.open("w", newline="") as fh:
            _write_header(fh, cal_sha, git_sha, seed, status)
            writer = csv.DictWriter(fh, fieldnames=COLUMNS)
            writer.writeheader()
            for scenario in scenarios:
                tau = cal["scenarios"][scenario]["tau"]
                for phi in tier_a["failure_inject"]:
                    for partition in tier_a["partition"]:
                        for trial in range(reps):
                            instances = generate_trial(
                                master_seed=seed, scenario=scenario, replicas=R,
                                cache_ratio=rho, failure_inject=phi, partition=partition,
                                trial=trial, calibration=cal,
                            )
                            disagree = neutro_bool_disagreement(instances, tau=tau)
                            for system in systems:
                                m = evaluate_trial(system, instances, tau=tau, replicas=R,
                                                   local_ms=local_ms)
                                writer.writerow({
                                    "calibration_sha256": cal_sha, "code_git_sha": git_sha,
                                    "random_seed": seed, "status": status,
                                    "scenario": scenario, "system": system, "replicas_R": R,
                                    "cache_ratio_rho": rho, "failure_inject_phi": phi,
                                    "partition": partition, "trial": trial,
                                    "n_decisions": m["n_decisions"], "n_acted": m["n_acted"],
                                    "n_stale": m["n_stale"],
                                    "stale_rate": f"{m['stale_rate']:.6f}",
                                    "availability": f"{m['availability']:.6f}",
                                    "failure_rate": f"{m['failure_rate']:.6f}",
                                    "messages_mean": m["messages_mean"],
                                    "mlat_p50": f"{m['mlat_p50']:.4f}",
                                    "mlat_p95": f"{m['mlat_p95']:.4f}",
                                    "mlat_p99": f"{m['mlat_p99']:.4f}",
                                    "i_occupancy": f"{m['i_occupancy']:.6f}",
                                    "neutro_bool_disagree": f"{disagree:.6f}",
                                })
        written.append(path)
        print(f"wrote {path}")
    return written


def main() -> None:
    ap = argparse.ArgumentParser(description="ns-dsl experiment harness")
    ap.add_argument("--quick", action="store_true", help="fast smoke run (1 seed, few reps)")
    args = ap.parse_args()
    run(quick=args.quick)


if __name__ == "__main__":
    main()
