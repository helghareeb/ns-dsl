"""THE single canonical aggregator (Rule R2). Every table and figure derives from its output.

Reads all hash-stamped raw per-trial CSVs, asserts they share one calibration SHA-256 (Rule R6),
and emits:
  results/tables/per_config_summary.csv  -- one row per (scenario, system, phi, partition) cell
                                            with bootstrap 95% CIs (Rule R12) and failure gating (R8)
  results/tables/pairwise_tests.csv      -- Holm-corrected (R3) paired Wilcoxon contrasts per family

No other script computes statistics.
"""
from __future__ import annotations

import glob
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests


def _cell_seed(scenario: str, system: str, phi, partition: str) -> int:
    """Deterministic per-cell bootstrap seed (stable across Python runs and independent of which/
    how many systems are in the run), so the bootstrap CIs are byte-reproducible (R1/R5)."""
    key = f"{scenario}|{system}|{phi}|{partition}".encode()
    return int.from_bytes(hashlib.sha256(key).digest()[:8], "big") % (2**32)

from .calibration import load_calibration

ROOT = Path(__file__).resolve().parents[1]
RAW_GLOB = str(ROOT / "results" / "raw" / "raw_*.csv")
TABLES = ROOT / "results" / "tables"

CELL_KEYS = ["scenario", "system", "failure_inject_phi", "partition"]
GROUP_KEYS = ["scenario", "failure_inject_phi", "partition"]   # a cell minus system


def load_raw(paths: list[str]) -> pd.DataFrame:
    frames, hashes = [], set()
    for p in paths:
        df = pd.read_csv(p, comment="#")
        frames.append(df)
        hashes.update(df["calibration_sha256"].unique())
    if len(hashes) != 1:
        raise SystemExit(f"REFUSING to mix CSVs with different calibration hashes: {hashes}")
    return pd.concat(frames, ignore_index=True)


def _bootstrap_ci(values: np.ndarray, n_boot: int, rng: np.random.Generator,
                  agg=np.mean, alpha=0.05) -> tuple[float, float]:
    if len(values) < 2:
        v = float(values[0]) if len(values) else float("nan")
        return v, v
    idx = rng.integers(0, len(values), size=(n_boot, len(values)))
    boot = agg(values[idx], axis=1)
    return float(np.quantile(boot, alpha / 2)), float(np.quantile(boot, 1 - alpha / 2))


def summarize(df: pd.DataFrame, calibration: dict) -> pd.DataFrame:
    n_boot = calibration["bootstrap_resamples"]
    gate = calibration["failure_rate_gate"]
    rows = []
    for keys, cell in df.groupby(CELL_KEYS, sort=True):
        scenario, system, phi, partition = keys
        rng = np.random.default_rng(_cell_seed(scenario, system, phi, partition))
        stale = cell["stale_rate"].to_numpy(float)
        avail = cell["availability"].to_numpy(float)
        fail = cell["failure_rate"].mean()
        s_lo, s_hi = _bootstrap_ci(stale, n_boot, rng)
        a_lo, a_hi = _bootstrap_ci(avail, n_boot, rng)
        p99 = cell["mlat_p99"].to_numpy(float)
        p99 = p99[~np.isnan(p99)]
        rows.append({
            "scenario": scenario, "system": system,
            "failure_inject_phi": phi, "partition": partition,
            "n_trials": len(cell),
            "stale_rate": stale.mean(), "stale_ci_lo": s_lo, "stale_ci_hi": s_hi,
            "availability": avail.mean(), "avail_ci_lo": a_lo, "avail_ci_hi": a_hi,
            "failure_rate": fail,
            "percentile_basis": "success_only" if fail > gate else "all",
            "messages_mean": cell["messages_mean"].mean(),
            "mlat_p50": cell["mlat_p50"].mean(),
            "mlat_p99": float(np.mean(p99)) if len(p99) else float("nan"),
            "i_occupancy": cell["i_occupancy"].mean(),
            "neutro_bool_disagree": cell["neutro_bool_disagree"].mean(),
            "status": cell["status"].iloc[0],
        })
    return pd.DataFrame(rows).sort_values(CELL_KEYS).reset_index(drop=True)


def _cohens_d_paired(a: np.ndarray, b: np.ndarray) -> float:
    d = a - b
    sd = d.std(ddof=1)
    return float(d.mean() / sd) if sd > 0 else 0.0


def pairwise_tests(df: pd.DataFrame, metric: str, family_id: str,
                   systems: list[str]) -> pd.DataFrame:
    """Paired Wilcoxon contrasts among ``systems`` per group, Holm-corrected within the family."""
    rows = []
    for keys, grp in df.groupby(GROUP_KEYS, sort=True):
        scenario, phi, partition = keys
        wide = grp.pivot_table(index=["random_seed", "trial"], columns="system", values=metric)
        present = [s for s in systems if s in wide.columns]
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                a, b = present[i], present[j]
                pair = wide[[a, b]].dropna()
                if len(pair) < 3:
                    continue
                av, bv = pair[a].to_numpy(), pair[b].to_numpy()
                try:
                    _, p = stats.wilcoxon(av, bv, zero_method="zsplit")
                except ValueError:
                    p = 1.0   # all-zero differences -> no detectable effect
                rows.append({
                    "family_id": family_id, "metric": metric, "scenario": scenario,
                    "failure_inject_phi": phi, "partition": partition,
                    "system_a": a, "system_b": b, "n_trials": len(pair),
                    "mean_a": av.mean(), "mean_b": bv.mean(),
                    "cohens_d": _cohens_d_paired(av, bv), "p_raw": p,
                })
    out = pd.DataFrame(rows)
    if not out.empty:
        out["p_holm"] = multipletests(out["p_raw"], method="holm")[1]
    return out


def multiseed_validation(df: pd.DataFrame, contrasts: list[tuple[str, str, str]]) -> pd.DataFrame:
    """For each headline contrast, check the effect replicates in sign across all seeds (N9/N14).

    A (scenario, phi, partition) cell is 'replicated' iff the sign of (mean_a - mean_b) agrees
    across every seed. Cells that do not replicate must be reported as provisional.
    """
    rows = []
    for metric, a, b in contrasts:
        for keys, grp in df.groupby(GROUP_KEYS, sort=True):
            scenario, phi, partition = keys
            per_seed = []
            for _seed, sg in grp.groupby("random_seed"):
                wide = sg.pivot_table(index="trial", columns="system", values=metric)
                if a in wide and b in wide:
                    per_seed.append(wide[a].mean() - wide[b].mean())
            if len(per_seed) < 2:
                continue
            signs = {(-1 if d < 0 else 1 if d > 0 else 0) for d in per_seed}
            rows.append({
                "metric": metric, "system_a": a, "system_b": b, "scenario": scenario,
                "failure_inject_phi": phi, "partition": partition, "n_seeds": len(per_seed),
                "mean_diff": sum(per_seed) / len(per_seed),
                "signs_agree": len(signs) == 1,
            })
    return pd.DataFrame(rows)


def main() -> None:
    cal = load_calibration()
    paths = sorted(glob.glob(RAW_GLOB))
    if not paths:
        raise SystemExit(f"no raw CSVs found at {RAW_GLOB}; run experiments/run_all.py first")
    raw = load_raw(paths)
    TABLES.mkdir(parents=True, exist_ok=True)

    summary = summarize(raw, cal)
    summary.to_csv(TABLES / "per_config_summary.csv", index=False)

    all_systems = ["neutro-waa", "neutro-wga", "quorum-bool", "centralized",
                   "raft-lww", "lww-crdt", "single-peer", "naive-cache"]
    families = [
        pairwise_tests(raw, "stale_rate", "F1_stale", all_systems),
        pairwise_tests(raw, "availability", "F4_availability", all_systems),
        pairwise_tests(raw, "stale_rate", "F3_ablation", ["neutro-waa", "neutro-wga"]),
    ]
    pairwise = pd.concat([f for f in families if not f.empty], ignore_index=True)
    pairwise.to_csv(TABLES / "pairwise_tests.csv", index=False)

    headline_contrasts = [
        ("stale_rate", "neutro-waa", "quorum-bool"),
        ("stale_rate", "neutro-waa", "lww-crdt"),
        ("availability", "neutro-waa", "centralized"),
    ]
    ms = multiseed_validation(raw, headline_contrasts)
    ms.to_csv(TABLES / "multiseed_validation.csv", index=False)

    print(f"summary   -> {TABLES / 'per_config_summary.csv'} ({len(summary)} cells)")
    print(f"pairwise  -> {TABLES / 'pairwise_tests.csv'} ({len(pairwise)} contrasts)")
    if not ms.empty:
        print(f"multiseed -> {TABLES / 'multiseed_validation.csv'} "
              f"({ms.signs_agree.mean() * 100:.0f}% of cells replicate across seeds)")
    print(f"calibration_sha256 = {raw['calibration_sha256'].iloc[0]}")


if __name__ == "__main__":
    main()
