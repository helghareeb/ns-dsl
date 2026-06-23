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

ORDER = ["centralized", "raft-lww", "neutro-waa", "neutro-wga", "quorum-bool", "prob-gate",
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
        ls = "--" if system == "raft-lww" else "-"   # raft-lww coincides with centralized at 0; dash reveals both
        ax.plot(s.failure_inject_phi, s.stale_rate, marker="o", linestyle=ls, label=system)
        ax.fill_between(s.failure_inject_phi, s.stale_ci_lo, s.stale_ci_hi, alpha=0.12)
    ax.set_xlabel("failure-injection rate $\\varphi$")
    ax.set_ylabel("stale-decision rate (acted)")
    ax.set_title(f"Stale-decision rate vs. failure rate ({scenario})")
    ax.legend(fontsize=7, loc="center left", bbox_to_anchor=(1.02, 0.5))   # outside axes: never over data
    _save(fig, "f2_stale_vs_phi")


def fig_pareto(df: pd.DataFrame, scenario: str = "S2", phi: float = 0.1) -> None:
    sub = df[(df.scenario == scenario) & (df.partition == "none")
             & (df.failure_inject_phi == phi)].set_index("system")
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    # distinct marker SHAPE per system so coincident points (centralized==raft-lww at (0,0.9)) layer visibly
    markers = {"centralized": "o", "raft-lww": "X", "neutro-waa": "*", "neutro-wga": "h",
               "quorum-bool": "s", "prob-gate": "p", "pbs-quorum": "D", "lww-crdt": "v",
               "single-peer": "^", "naive-cache": "d"}
    for sysname in ORDER:
        if sysname not in sub.index:
            continue
        r = sub.loc[sysname]
        big = sysname.startswith("neutro")
        size = 200 if big else (130 if sysname == "centralized" else 70)   # centralized larger so it peeks out under raft-lww 'X'
        ax.scatter(r.stale_rate, r.availability, s=size, marker=markers.get(sysname, "o"),
                   edgecolors="black", linewidths=0.5, label=sysname, zorder=3)
    ax.set_xlabel("stale-decision rate (lower is better)")
    ax.set_ylabel("availability (higher is better)")
    ax.set_title(f"Correctness/availability trade-off ({scenario}, $\\varphi$={phi})")
    ax.legend(fontsize=7, loc="center left", bbox_to_anchor=(1.02, 0.5),   # outside axes: never over data
              labelspacing=0.8, handletextpad=0.6, borderpad=0.8, framealpha=0.9)
    ax.grid(True, alpha=0.2)
    _save(fig, "f3_pareto")


def fig_throughput() -> None:
    path = ROOT / "results" / "tables" / "throughput.csv"
    if not path.exists():
        return
    d = pd.read_csv(path).set_index("system")
    systems = [s for s in ORDER if s in d.index]
    fig, ax = plt.subplots(figsize=(7, 4))
    vals = [d.throughput_dps.get(s, 0) for s in systems]
    bars = ax.bar(range(len(systems)), vals)
    ax.set_yscale("log")                       # naive (local) dwarfs network strategies otherwise
    ax.set_xticks(range(len(systems)))
    ax.set_xticklabels(systems, rotation=20, fontsize=8)
    ax.set_ylabel("throughput (decisions/sec, log scale)")
    ax.set_title("Measured throughput under concurrent load (real HTTP testbed)")
    ax.bar_label(bars, fmt="%.0f", fontsize=7, padding=2)
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
    ax.legend(fontsize=8, loc="center left", bbox_to_anchor=(1.02, 0.5))   # outside axes: never over bars
    _save(fig, "f7_availability_partition")


def fig_signal_richness(df: pd.DataFrame, phi: float = 0.1) -> None:
    """RQ1: how often the (T,I,F) decision diverges from a boolean quorum, per scenario."""
    sub = df[(df.partition == "none") & (df.failure_inject_phi == phi)
             & (df.system == "neutro-waa")].sort_values("scenario")
    fig, ax = plt.subplots(figsize=(5.5, 3.6))
    ax.bar(sub.scenario, sub.neutro_bool_disagree, width=0.5, label="neutro vs. boolean disagreement")
    ax.plot(sub.scenario, sub.i_occupancy, "o--", color="C1", label="mean indeterminacy (cache) occupancy")
    ax.set_ylabel("fraction of decisions")
    ax.set_ylim(0, 0.75)
    ax.set_title(f"Signal richness of the $(T,I,F)$ axis ($\\varphi={phi}$)")
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)   # below axes: never over bars
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
    ax.set_yscale("log")                       # naive-cache is a local read (~0.02 ms); dwarfed otherwise
    ax.set_ylim(bottom=0.01)
    ax.set_xticks(range(len(systems)))
    ax.set_xticklabels(systems, rotation=20, fontsize=8)
    ax.set_ylabel("measured decision latency p50 (ms, log scale)")
    ax.set_title("Measured latency on the real HTTP testbed (localhost)")
    ax.legend(fontsize=8, loc="center left", bbox_to_anchor=(1.02, 0.5))   # outside axes: never over bars
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
    # recovery_fraction and wga_accept_rate coincide (WGA accepts exactly when the clone is recovered);
    # distinct linestyles/widths so all three series are visible
    ax.plot(d.events_replayed, d.recovery_fraction, "-", lw=3.5, alpha=0.55, color="C0", label="state recovered")
    ax.plot(d.events_replayed, d.wga_accept_rate, "--", lw=1.6, color="C1", label="cluster accept (SVNNWGA)")
    ax.plot(d.events_replayed, d.waa_accept_rate, ":", lw=2.2, color="C2", label="cluster accept (SVNNWAA)")
    ax.set_xlabel("log events replayed by the fresh clone")
    ax.set_ylabel("fraction")
    ax.set_ylim(-0.05, 1.08)
    ax.set_title("S3 clone catch-up via log replay")
    ax.legend(fontsize=8, loc="lower right")   # empty corner: below the rising diagonal
    _save(fig, "f9_s3_convergence")


# --- enrichment figures (read result CSVs only; no simulation) -----------------------------

OPERATOR_PANEL = ["neutro-waa-g", "neutro-wga-g", "neutro-einstein-g", "neutro-hamacher-g",
                  "neutro-dombi-g", "neutro-aczel_alsina-g", "neutro-bonferroni-g",
                  "neutro-median-g", "neutro-trimmed-g", "neutro-krum-g"]


def fig_operator_pareto(df: pd.DataFrame, scenario: str = "S2", phi: float = 0.1) -> None:
    """Axis A: the graded operator panel spreads the correctness/availability frontier."""
    sub = df[(df.scenario == scenario) & (df.partition == "none")
             & (df.failure_inject_phi == phi)].set_index("system")
    fig, ax = plt.subplots(figsize=(6.5, 4.4))
    for s in ("lww-crdt", "quorum-bool", "centralized"):       # reference baselines
        if s in sub.index:
            r = sub.loc[s]
            ax.scatter(r.stale_rate, r.availability, s=70, marker="s", color="0.5", zorder=2)
            ax.annotate(s, (r.stale_rate, r.availability), fontsize=6, color="0.4")
    for s in OPERATOR_PANEL:
        if s not in sub.index:
            continue
        r = sub.loc[s]
        ax.scatter(r.stale_rate, r.availability, s=120, marker="o", zorder=3,
                   label=s.replace("neutro-", "").replace("-g", ""))
    ax.set_xlabel("stale-decision rate (lower is better)")
    ax.set_ylabel("availability (higher is better)")
    ax.set_title(f"Operator panel spreads the frontier ({scenario}, $\\varphi$={phi})")
    ax.legend(fontsize=7, ncol=2, loc="lower left", title="graded operator")
    ax.grid(True, alpha=0.2)
    _save(fig, "f11_operator_pareto")


def fig_byzantine() -> None:
    """Honest Byzantine result: robust aggregators degrade together with the averaging operator
    under value-fabrication (robust aggregation defends the gate, not value-selection)."""
    path = ROOT / "results" / "tables" / "byzantine.csv"
    if not path.exists():
        return
    d = pd.read_csv(path)
    systems = ["neutro-waa-g", "neutro-median-g", "neutro-krum-g", "neutro-trimmed-g",
               "quorum-bool", "lww-crdt"]
    fig, ax = plt.subplots(figsize=(6, 4))
    for s in systems:
        ss = d[d.system == s].sort_values("byzantine_frac")
        if ss.empty:
            continue
        style = "-o" if "median" in s or "krum" in s or "trimmed" in s else "--s"
        ax.plot(ss.byzantine_frac, ss.stale_rate, style, label=s.replace("neutro-", ""))
    ax.set_xlabel("Byzantine peer fraction")
    ax.set_ylabel("stale-decision rate (acted)")
    ax.set_title("Byzantine value-fabrication: robust $\\approx$ averaging (S2, $\\varphi$=0.1)")
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.2)
    _save(fig, "f12_byzantine")


def fig_scalability() -> None:
    """Scalability: stale-rate improves with R at linear message cost; availability maintained."""
    path = ROOT / "results" / "tables" / "scalability.csv"
    if not path.exists():
        return
    d = pd.read_csv(path)
    systems = ["neutro-waa-g", "neutro-median-g", "quorum-bool", "lww-crdt", "centralized"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    for s in systems:
        ss = d[d.system == s].sort_values("replicas")
        if ss.empty:
            continue
        axes[0].plot(ss.replicas, ss.stale_rate, marker="o", label=s.replace("neutro-", ""))
        axes[1].plot(ss.replicas, ss.availability, marker="o", label=s.replace("neutro-", ""))
    axes[0].set_xlabel("replicas $R$"); axes[0].set_ylabel("stale-decision rate")
    axes[1].set_xlabel("replicas $R$"); axes[1].set_ylabel("availability")
    from matplotlib.ticker import ScalarFormatter, NullFormatter
    rvals = sorted(d.replicas.unique())
    for ax in axes:
        ax.set_xscale("log")
        ax.set_xticks(rvals)
        ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.xaxis.set_minor_formatter(NullFormatter())
    axes[1].legend(fontsize=7)
    fig.suptitle("Scalability with cluster size (S2, $\\varphi$=0.1)")
    _save(fig, "f13_scalability")


def fig_wan_latency() -> None:
    """D': measured decision-latency tails under emulated WAN (Toxiproxy latency+jitter+loss)."""
    path = ROOT / "results" / "tables" / "wan_latency.csv"
    if not path.exists():
        return
    d = pd.read_csv(path)
    profiles = [p for p in ["lan", "regional", "wan", "wan-lossy"] if p in set(d.profile)]
    patterns = ["1-hop", "majority", "R-fan-out"]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    width = 0.8 / len(patterns)
    for k, pat in enumerate(patterns):
        sub = d[d.pattern == pat].set_index("profile")
        xs = [i + (k - len(patterns) / 2 + 0.5) * width for i in range(len(profiles))]
        p50 = [sub.p50_ms.get(p, float("nan")) for p in profiles]
        p99 = [sub.p99_ms.get(p, float("nan")) for p in profiles]
        ax.bar(xs, p50, width=width, label=pat)
        err = [max(0.0, b - a) for a, b in zip(p50, p99)]   # p99 cap above the p50 bar
        ax.errorbar(xs, p50, yerr=[[0.0] * len(p50), err], fmt="none", ecolor="0.25", capsize=2, lw=0.8)
    ax.set_yscale("log")
    ax.set_xticks(range(len(profiles)))
    ax.set_xticklabels(profiles)
    ax.set_ylabel("decision latency (ms, log scale)")
    ax.set_title("Emulated-WAN decision latency: p50 (bar), p99 (cap)")
    ax.legend(fontsize=8, title="wait pattern")
    _save(fig, "f14_wan_latency")


def fig_tuning() -> None:
    """Axis-B: equal-budget tuning is optimizer-agnostic (No Free Lunch); beats uniform only on S2."""
    path = ROOT / "results" / "tables" / "weight_tuning.csv"
    base = ROOT / "results" / "tables" / "weight_tuning_baseline.csv"
    if not path.exists() or not base.exists():
        return
    d = pd.read_csv(path)
    b = pd.read_csv(base).set_index("scenario")
    scenarios = [s for s in ["S1", "S2", "S3"] if s in set(d.scenario)]
    fig, axes = plt.subplots(1, len(scenarios), figsize=(9.5, 3.4))
    for ax, sc in zip(axes, scenarios):
        sub = d[d.scenario == sc].sort_values("utility", ascending=False)
        ax.scatter(range(len(sub)), sub.utility, s=55, zorder=3, color="C0", label="optimizers (tuned)")
        ax.axhline(b.uniform_utility[sc], ls="--", color="C3", label="uniform weights")
        ax.set_xticks(range(len(sub)))
        ax.set_xticklabels(sub.optimizer, rotation=60, fontsize=7)
        ax.set_title(sc)
        ax.set_ylabel("utility (avail $-$ cost$\\cdot$stale)" if sc == scenarios[0] else "")
        ax.grid(True, axis="y", alpha=0.2)
    axes[-1].legend(fontsize=7, loc="best")
    fig.suptitle("Axis-B: tuning is optimizer-agnostic; it beats uniform weights only under asymmetric cost (S2)")
    _save(fig, "f15_tuning")


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
    fig_operator_pareto(df)
    fig_byzantine()
    fig_scalability()
    fig_wan_latency()
    fig_tuning()
    print(f"figures -> {FIGDIR}")


if __name__ == "__main__":
    main()
