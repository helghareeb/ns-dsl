"""Print the headline numbers cited in the manuscript, from the canonical outputs.

Convenience for keeping the manuscript prose in sync with the validated results (Rule R1/R2).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

T = Path(__file__).resolve().parents[1] / "results" / "tables"


def _cell(s, scenario, system, phi, part):
    r = s[(s.scenario == scenario) & (s.system == system)
          & (s.failure_inject_phi == phi) & (s.partition == part)]
    return r.iloc[0] if len(r) else None


def main() -> None:
    s = pd.read_csv(T / "per_config_summary.csv")
    pw = pd.read_csv(T / "pairwise_tests.csv")
    ms = pd.read_csv(T / "multiseed_validation.csv")
    print(f"cells={len(s)}  status={dict(s.status.value_counts())}  "
          f"multiseed_replicate={ms.signs_agree.mean()*100:.0f}%")

    for sc in ("S1", "S2", "S3"):
        for part in ("none", "transient"):
            waa = _cell(s, sc, "neutro-waa", 0.1, part)
            if waa is None:
                continue
            lww = _cell(s, sc, "lww-crdt", 0.1, part)
            naive = _cell(s, sc, "naive-cache", 0.1, part)
            cen = _cell(s, sc, "centralized", 0.1, part)
            qb = _cell(s, sc, "quorum-bool", 0.1, part)
            pbs = _cell(s, sc, "pbs-quorum", 0.1, part)
            print(f"\n[{sc} phi=0.1 {part}] neutro-waa stale={waa.stale_rate:.3f} "
                  f"avail={waa.availability:.3f}")
            for name, r in [("lww", lww), ("naive", naive), ("pbs", pbs), ("quorum", qb)]:
                if r is not None and r.stale_rate > 0:
                    red = (1 - waa.stale_rate / r.stale_rate) * 100
                    print(f"   vs {name}: stale {r.stale_rate:.3f} (reduction {red:+.0f}%), "
                          f"avail {r.availability:.3f}")
            if cen is not None:
                print(f"   vs centralized: stale {cen.stale_rate:.3f} avail {cen.availability:.3f}")

    print("\n-- headline Holm contrasts (S2, phi=0.1) --")
    key = pw[(pw.scenario == "S2") & (pw.failure_inject_phi == 0.1)]
    for _, r in key.iterrows():
        pair = {r.system_a, r.system_b}
        if pair in ({"neutro-waa", "lww-crdt"}, {"neutro-waa", "centralized"},
                    {"neutro-waa", "quorum-bool"}, {"neutro-waa", "pbs-quorum"}):
            print(f"   [{r.partition:9s}] {r.metric}: {r.system_a} vs {r.system_b} "
                  f"d={r.cohens_d:+.2f} p_holm={r.p_holm:.1e}")

    for extra, label in [("latency_measured.csv", "latency (rtt=5ms p50)"),
                         ("throughput.csv", "throughput (dec/s)")]:
        p = T / extra
        if p.exists():
            d = pd.read_csv(p)
            print(f"\n-- {label} --")
            if "rtt_ms" in d.columns:
                d = d[d.rtt_ms == 5.0]
                for _, r in d.iterrows():
                    print(f"   {r.system:12s} {r.p50_ms:.1f}")
            else:
                for _, r in d.sort_values('throughput_dps', ascending=False).iterrows():
                    print(f"   {r.system:12s} {r.throughput_dps:.0f}")


if __name__ == "__main__":
    main()
