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
         "pbs-quorum", "lww-crdt", "single-peer", "naive-cache"]


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
             & (df.failure_inject_phi == phi)].set_index("system")
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    markers = {"neutro-waa": "*", "neutro-wga": "*"}
    for sysname in ORDER:
        if sysname not in sub.index:
            continue
        r = sub.loc[sysname]
        ax.scatter(r.stale_rate, r.availability, s=140 if sysname.startswith("neutro") else 60,
                   marker=markers.get(sysname, "o"), label=sysname, zorder=3)
    ax.set_xlabel("stale-decision rate (lower is better)")
    ax.set_ylabel("availability (higher is better)")
    ax.set_title(f"Correctness/availability trade-off ({scenario}, $\\varphi$={phi})")
    ax.legend(fontsize=7, ncol=2, loc="lower left")
    ax.grid(True, alpha=0.2)
    _save(fig, "f3_pareto")


def fig_throughput() -> None:
    path = ROOT / "results" / "tables" / "throughput.csv"
    if not path.exists():
        return
    d = pd.read_csv(path).set_index("system")
    systems = [s for s in ORDER if s in d.index]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(range(len(systems)), [d.throughput_dps.get(s, 0) for s in systems])
    ax.set_xticks(range(len(systems)))
    ax.set_xticklabels(systems, rotation=20, fontsize=8)
    ax.set_ylabel("throughput (decisions/sec)")
    ax.set_title("Measured throughput under concurrent load (real HTTP testbed)")
    _save(fig, "f10_throughput")


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


def fig_signal_richness(df: pd.DataFrame, phi: float = 0.1) -> None:
    """RQ1: how often the (T,I,F) decision diverges from a boolean quorum, per scenario."""
    sub = df[(df.partition == "none") & (df.failure_inject_phi == phi)
             & (df.system == "neutro-waa")].sort_values("scenario")
    fig, ax = plt.subplots(figsize=(5.5, 3.6))
    ax.bar(sub.scenario, sub.neutro_bool_disagree, width=0.5, label="neutro vs.\\ boolean disagreement")
    ax.plot(sub.scenario, sub.i_occupancy, "o--", color="C1", label="mean indeterminacy (cache) occupancy")
    ax.set_ylabel("fraction of decisions")
    ax.set_title(f"Signal richness of the $(T,I,F)$ axis ($\\varphi={phi}$)")
    ax.legend(fontsize=8)
    _save(fig, "f8_signal_richness")


def fig_latency_measured() -> None:
    path = ROOT / "results" / "tables" / "latency_measured.csv"
    if not path.exists():
        return
    d = pd.read_csv(path)
    rtts = sorted(d.rtt_ms.unique())
    systems = [s for s in ORDER if s in set(d.system)]
    fig, ax = plt.subplots(figsize=(7, 4))
    width = 0.8 / len(rtts)
    for k, rtt in enumerate(rtts):
        sub = d[d.rtt_ms == rtt].set_index("system")
        xs = [i + (k - len(rtts) / 2) * width for i in range(len(systems))]
        ax.bar(xs, [sub.p50_ms.get(s, 0) for s in systems], width=width, label=f"RTT={rtt:g}ms")
    ax.set_xticks(range(len(systems)))
    ax.set_xticklabels(systems, rotation=20, fontsize=8)
    ax.set_ylabel("measured decision latency p50 (ms)")
    ax.set_title("Measured latency on the real HTTP testbed (localhost)")
    ax.legend(fontsize=8)
    _save(fig, "f5_latency_measured")


def fig_sensitivity() -> None:
    path = ROOT / "results" / "tables" / "sensitivity.csv"
    if not path.exists():
        return
    d = pd.read_csv(path)
    systems = ["neutro-waa", "quorum-bool", "lww-crdt", "centralized"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    for ax, factor, xlabel in [(axes[0], "replicas", "replicas $R$"),
                               (axes[1], "cache_ratio", "cache ratio $\\rho$")]:
        sub = d[d.factor == factor]
        for s in systems:
            ss = sub[sub.system == s].sort_values("value")
            ax.plot(ss.value, ss.stale_rate, marker="o", label=s)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("stale-decision rate")
    axes[1].legend(fontsize=7)
    fig.suptitle("Sensitivity of stale-decision rate (S2, $\\varphi=0.1$)")
    _save(fig, "f6_sensitivity")


def fig_s3_convergence() -> None:
    path = ROOT / "results" / "tables" / "s3_convergence.csv"
    if not path.exists():
        return
    d = pd.read_csv(path)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(d.events_replayed, d.recovery_fraction, marker=".", label="state recovered")
    ax.plot(d.events_replayed, d.wga_accept_rate, marker=".", label="cluster accept (SVNNWGA)")
    ax.plot(d.events_replayed, d.waa_accept_rate, marker=".", label="cluster accept (SVNNWAA)")
    ax.set_xlabel("log events replayed by the fresh clone")
    ax.set_ylabel("fraction")
    ax.set_title("S3 clone catch-up via log replay")
    ax.legend(fontsize=8)
    _save(fig, "f9_s3_convergence")


def main() -> None:
    if not SUMMARY.exists():
        raise SystemExit(f"missing {SUMMARY}; run experiments/analyze_results.py first")
    df = pd.read_csv(SUMMARY)
    fig_stale_vs_phi(df)
    fig_pareto(df)
    fig_availability_partition(df)
    fig_signal_richness(df)
    fig_latency_measured()
    fig_sensitivity()
    fig_s3_convergence()
    fig_throughput()
    print(f"figures -> {FIGDIR}")


if __name__ == "__main__":
    main()
