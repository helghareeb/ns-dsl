# Review-response progress ledger (2026-06-23)

Status of the two-reviewer Q1 enhancement + author scope decisions. Venue = **Scientific Reports**.
Every change is committed to `main`; this ledger is the single status view.

## Done & committed
- **Figures**: 6 reported defects fixed + Fig 4 round-2 (neutro-wga hexagon marker, legend spacing).
  All regenerate from `results/tables/*.csv` (no re-run). Verified by reading each PDF.
- **Statements**: Code-availability corrected to the private-repo wording (was wrongly "open-source MIT
  in the repository"); Data-availability aligned to deferred release; Author-contributions, Competing
  interests, Funding, and an LLM-use disclosure added. *(LLM wording flagged for your sign-off.)*
- **Bucket A (presentation)**: amsthm theorem environments; abstract 336→~230 w (final ≤200 in SR-polish);
  complexity analysis (O(|R|)); explicit graded-encoding anchor table; **stats accuracy fixes** (the audit
  caught real errors: Methods said 3 seeds / ≥30 reps / φ∈{0,0.1,0.3} → corrected to 5 seeds / 50 reps /
  250 reps-per-cell / φ∈{0,0.1,0.2,0.3}); unit-of-analysis clarified (paired at the repetition level,
  n=250, not per-decision); percentage-point effect sizes; full calibration SHA-256 printed; novelty-vs-2020
  enumeration (a–d) with the operator panel framed as generality; threats expanded (workload validity,
  dynamic membership/churn, event-bus overhead, softened latency tone); dedicated future-work paragraph.
- **Bucket C (theory, HONEST)**: lemmas generalized to the graded encoding + tuned weights (monotonicity
  + bounded-staleness corollary); Byzantine gate lemma tightened; **new Proposition: value-selection is
  NOT Byzantine-robust** (matches the empirical null — no false "robust wins"); new committed-value safety
  theorem.
- **Bucket B (code)**: `prob-gate` Bayesian single-probability gate baseline implemented, registered,
  τ-calibrated, message/latency-classed; tests updated (all green).
- **Bucket D′ (infra)**: `docker/docker-compose.wan.yml` + `bench/wan_latency.py` — Toxiproxy emulated-WAN
  tail-latency harness (LAN/regional/WAN/lossy profiles; p50/p95/p99/p99.9). Compiles; compose validates.
- **Title**: "…in microservices architectures" (your addition).

## Running (background; will auto-resume integration on completion)
- **prob-gate grid** (`bkkgmc9b3`): calibrate → full grid → analyze. Adds prob-gate to
  `per_config_summary.csv`; existing systems reproduce identically (deterministic). → then I write the
  "(T,I,F) is not a relabelled probability" Results contrast.
- **metaheuristic tune** (`bsg4bos64`): full-budget Axis-B run → `weight_tuning.csv`. → then the Axis-B
  tuning subsection + figure.

## Next (gated on the above + a free laptop)
1. Integrate prob-gate Results contrast (when grid lands).
2. Integrate Axis-B tuning subsection (when tune lands).
3. **Run + VERIFY** the D′ emulated-WAN study (stable repeat run before any number enters the paper, N6).
4. **4th scenario** — ML feature-store / online-feature freshness (default; *flagged for you to redirect
   to IoT/edge*); re-run grid; integrate as a generality result.
5. **SR-polish**: wlscirep template, restructure (Intro→Results→Discussion→Methods), ≤8 display items +
   Supplementary, abstract ≤200 final, Nature refs/.bbl, cover letter, submission package.

## Flagged for your sign-off (non-blocking)
- LLM-use disclosure exact wording.
- 3 suggested reviewers for the cover letter.
- 4th-scenario domain (feature-store default vs IoT/edge).
