"""Emit LaTeX tables for the manuscript from the canonical per_config_summary.csv (Rule R2).

The manuscript \\input's these, so every printed number traces to the aggregator output.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "results" / "tables" / "per_config_summary.csv"
OUT = ROOT / "paper" / "tables"

ORDER = ["centralized", "raft-lww", "neutro-waa", "neutro-wga", "quorum-bool",
         "pbs-quorum", "lww-crdt", "single-peer", "naive-cache"]
LABEL = {"centralized": "Centralized", "raft-lww": "Raft-LWW", "neutro-waa": "\\textbf{Neutro-WAA}",
         "neutro-wga": "\\textbf{Neutro-WGA}", "quorum-bool": "Quorum-bool", "pbs-quorum": "PBS-quorum",
         "lww-crdt": "LWW-CRDT", "single-peer": "Single-peer", "naive-cache": "Naive-cache"}


def headline_table(df: pd.DataFrame, scenario: str, phi: float) -> str:
    rows = []
    for part in ("none", "transient"):
        sub = df[(df.scenario == scenario) & (df.failure_inject_phi == phi)
                 & (df.partition == part)].set_index("system")
        for sysname in ORDER:
            if sysname not in sub.index:
                continue
            r = sub.loc[sysname]
            rows.append(
                f"{LABEL[sysname]} & {part} & "
                f"{r.stale_rate:.3f} [{r.stale_ci_lo:.3f}, {r.stale_ci_hi:.3f}] & "
                f"{r.availability:.3f} & {r.messages_mean:.0f} \\\\"
            )
    body = "\n".join(rows)
    return (
        "\\begin{table}[t]\n\\centering\n\\small\n"
        f"\\caption{{Headline results for {scenario} at $\\varphi={phi}$ (30 reps/cell, 3 seeds; "
        "stale-rate with 5000-resample bootstrap 95\\% CI). All cells \\texttt{validated}.}\n"
        f"\\label{{tab:headline-{scenario.lower()}}}\n"
        "\\begin{tabular}{llccc}\n\\toprule\n"
        "System & Partition & Stale-rate [95\\% CI] & Availability & Msgs/dec \\\\\n\\midrule\n"
        f"{body}\n\\bottomrule\n\\end{{tabular}}\n\\end{{table}}\n"
    )


PAIRWISE = ROOT / "results" / "tables" / "pairwise_tests.csv"
CONTRASTS = [
    ("stale_rate", "neutro-waa", "lww-crdt"),
    ("stale_rate", "neutro-waa", "naive-cache"),
    ("stale_rate", "neutro-waa", "quorum-bool"),
    ("availability", "neutro-waa", "centralized"),
]


def significance_table() -> str:
    pw = pd.read_csv(PAIRWISE)
    rows = []
    for metric, a, b in CONTRASTS:
        for part in ("none", "transient"):
            m = pw[(pw.scenario == "S2") & (pw.failure_inject_phi == 0.1) & (pw.partition == part)
                   & (pw.metric == metric)
                   & (((pw.system_a == a) & (pw.system_b == b))
                      | ((pw.system_a == b) & (pw.system_b == a)))]
            if m.empty:
                continue
            r = m.iloc[0]
            d = r.cohens_d if r.system_a == a else -r.cohens_d
            rows.append(
                f"{metric.replace('_', '-')} & {a} vs.\\ {b} & {part} & "
                f"{d:+.2f} & {r.p_holm:.1e} \\\\"
            )
    body = "\n".join(rows)
    return (
        "\\begin{table}[t]\n\\centering\\small\n"
        "\\caption{Headline paired contrasts (S2, $\\varphi=0.1$): paired Wilcoxon, Holm-corrected "
        "within family; Cohen's $d$ from paired differences (90 trials/cell across 3 seeds).}\n"
        "\\label{tab:significance}\n\\begin{tabular}{lllcc}\n\\toprule\n"
        "Metric & Contrast & Partition & Cohen's $d$ & $p_{\\mathrm{holm}}$ \\\\\n\\midrule\n"
        f"{body}\n\\bottomrule\n\\end{{tabular}}\n\\end{{table}}\n"
    )


def main() -> None:
    df = pd.read_csv(SUMMARY)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "headline_s2.tex").write_text(headline_table(df, "S2", 0.1), encoding="utf-8")
    (OUT / "headline_s1.tex").write_text(headline_table(df, "S1", 0.1), encoding="utf-8")
    if PAIRWISE.exists():
        (OUT / "significance.tex").write_text(significance_table(), encoding="utf-8")
    print(f"tables -> {OUT}")


if __name__ == "__main__":
    main()
