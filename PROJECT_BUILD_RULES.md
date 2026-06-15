# Project Build Rules — `ns-dsl` (FGCS extended paper)

This repo follows the author's standing research-methodology orders. The rule blocks that govern
this project are recorded here (Rule G4 — everything in the repo, version-controlled, survivable
beyond any single tooling session). The canonical, always-on copy lives in `~/.claude/CLAUDE.md`;
this file is the in-repo mirror of the rules that apply here.

## Universal (G)
- **G2 — Snapshots.** Commit after every coherent unit of work; long runs flush periodically.
- **G4 — Everything in the repo.** Plans, methodology, continuity ledgers live here, not only in
  tooling metadata folders.
- **G5 — Continuous commit/push.** Small commits, conventional messages, push when a remote exists.
  Large generated data is gitignored; generators + download links preserve reproducibility.

## Research methodology (R / N) — the Q1 backbone
- **R1 Inadmissibility.** No number appears in the paper unless it is regenerable end-to-end from
  committed code + `config/calibration.json` + a recorded seed.
- **R2 Single canonical aggregator.** All tables/figures derive from `experiments/analyze_results.py`
  → `results/per_config_summary.csv`. No second-source statistics.
- **R3 Holm correction** on all pairwise tests (within a-priori families); emit `p_raw` + `p_holm`.
- **R4 REPS ≥ 30** repetitions per configuration cell for headline numbers (target 50 for tails).
- **R5 Per-cell deterministic seed** = `uint64(SHA-256(RANDOM_SEED | canonical_cell_tuple))`.
  Environment RNG (arrivals/faults/clone timing) uses a **system-independent** sub-seed → paired design.
- **R6 Calibration SHA-256** of `config/calibration.json` embedded in every results CSV header;
  the aggregator refuses to mix CSVs with different hashes.
- **R8 Success-only percentiles** when a cell's failure rate exceeds 5%; failure rate reported as a
  co-primary metric.
- **R10 Run from project root** with `PYTHONPATH=src:.`.
- **R12 Bootstrap = 5000 resamples** for CIs on Cohen's d and headline percentages.
- **N3 Mandatory Conclusion** distinct from Discussion.
- **N5 Section order:** Title → Abstract → Introduction → Related Work → Methods → Results →
  Discussion → Threats to Validity (separate) → Conclusion → Data availability → Code availability →
  References.
- **N6 / N12 Strongest honest claim.** No superiority claim without evidence. Frame as "reveals
  previously-collapsed signals" / "reduces stale-decision rate by X% (Holm-corrected, bootstrap CI)".
- **N9 Multi-seed validation** (≥3 master seeds). **N14 validated vs provisional** tag in every
  results-file header; provisional results never enter the manuscript.
- **N2 / N10 Continuity docs:** `paper/RUNNING_JOBS.md`, `paper/Q1_HANDOFF.md`,
  `paper/LOCAL_EXECUTION_PLAYBOOK.md`, `paper/related_work_scan.md`.

## Project-specific honest-claim guardrails
- The neutrosophic layer is a **per-item freshness/consistency decision layer**, NOT a
  replication/consensus protocol. Never claim it "beats Raft/Paxos on consensus." The
  apples-to-apples control is **quorum-of-booleans**.
- `centralized` (strongly consistent) = correctness ceiling; `naive-cache` = correctness/latency
  floor. Our result is a **Pareto-interior tradeoff**, stated as such.
