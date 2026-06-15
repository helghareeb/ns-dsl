"""Regenerate paper figures from the canonical per_config_summary.csv (Rule R2).

Figures are written to results/figures/ as both PDF (for the manuscript) and PNG (for quick
viewing). This script reads ONLY the aggregator's output -- it computes no statistics.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "results" / "tables" / "per_config_summary.csv"
FIGDIR = ROOT / "results" / "figures"

ORDER = ["centralized", "raft-lww", "neutro-waa", "neutro-wga", "quorum-bool",
         "lww-crdt", "single-peer", "naive-cache"]


def _save(fig, name: str) -> None:
    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGDIR / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIGDIR / f"{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_stale_vs_phi(df: pd.DataFrame, scenario: str = "S2") -> None:
    sub = df[(df.scenario == scenario) & (df.partition == "none")]
    fig, ax = plt.subplots(figsize=(6, 4))
    for system in ORDER:
        s = sub[sub.system == system].sort_values("failure_inject_phi")
        if s.empty:
            continue
        ax.plot(s.failure_inject_phi, s.stale_rate, marker="o", label=system)
        ax.fill_between(s.failure_inject_phi, s.stale_ci_lo, s.stale_ci_hi, alpha=0.12)
    ax.set_xlabel("failure-injection rate $\\varphi$")
    ax.set_ylabel("stale-decision rate (acted)")
    ax.set_title(f"Stale-decision rate vs. failure rate ({scenario})")
    ax.legend(fontsize=7, ncol=2)
    _save(fig, "f2_stale_vs_phi")


def fig_pareto(df: pd.DataFrame, scenario: str = "S2", phi: float = 0.1) -> None:
    sub = df[(df.scenario == scenario) & (df.partition == "none")
             & (df.failure_inject_phi == phi)]
    fig, ax = plt.subplots(figsize=(6, 4))
    for _, r in sub.iterrows():
        ax.scatter(r.stale_rate, r.availability, s=60)
        ax.annotate(r.system, (r.stale_rate, r.availability), fontsize=7,
                    xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel("stale-decision rate (lower is better)")
    ax.set_ylabel("availability (higher is better)")
    ax.set_title(f"Correctness/availability trade-off ({scenario}, $\\varphi$={phi})")
    _save(fig, "f3_pareto")


def fig_availability_partition(df: pd.DataFrame, scenario: str = "S2", phi: float = 0.1) -> None:
    systems = ["centralized", "raft-lww", "neutro-waa", "quorum-bool", "lww-crdt"]
    none = df[(df.scenario == scenario) & (df.failure_inject_phi == phi)
              & (df.partition == "none")].set_index("system")
    part = df[(df.scenario == scenario) & (df.failure_inject_phi == phi)
              & (df.partition == "transient")].set_index("system")
    fig, ax = plt.subplots(figsize=(6, 4))
    x = range(len(systems))
    ax.bar([i - 0.2 for i in x], [none.availability.get(s, 0) for s in systems],
           width=0.4, label="no partition")
    ax.bar([i + 0.2 for i in x], [part.availability.get(s, 0) for s in systems],
           width=0.4, label="transient partition")
    ax.set_xticks(list(x))
    ax.set_xticklabels(systems, rotation=20, fontsize=8)
    ax.set_ylabel("availability")
    ax.set_title(f"Availability under partition ({scenario}, $\\varphi$={phi})")
    ax.legend(fontsize=8)
    _save(fig, "f7_availability_partition")


def main() -> None:
    if not SUMMARY.exists():
        raise SystemExit(f"missing {SUMMARY}; run experiments/analyze_results.py first")
    df = pd.read_csv(SUMMARY)
    fig_stale_vs_phi(df)
    fig_pareto(df)
    fig_availability_partition(df)
    print(f"figures -> {FIGDIR}")


if __name__ == "__main__":
    main()
