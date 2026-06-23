# Review-response progress ledger (updated 2026-06-23)

Two-reviewer Q1 enhancement + author scope decisions. Venue = **Scientific Reports**. Manuscript builds
clean at every step (32 pp, 0 errors/undefined). Everything committed to `main`.

## DONE & committed
- **Figures (7):** 6 reported defects fixed + Fig 4 round-2 (hexagon marker, legend spacing). All from
  committed CSVs.
- **Statements:** Code-availability corrected to the private-repo wording; Data/Author/Competing/Funding
  + LLM-use disclosure added (*LLM wording awaits your sign-off*).
- **Bucket A (presentation):** amsthm theorem environments; abstract 336→232 w (final ≤200 in SR-polish);
  `O(|R|)` complexity; graded-encoding anchor table; **stats accuracy fixes** (5 seeds / 50 reps / 250
  per cell / φ∈{0,0.1,0.2,0.3} — corrected real errors); unit-of-analysis = per-repetition; pp effect
  sizes; full calibration SHA-256; novelty-vs-2020 enumeration (a–d); threats expansion; future-work.
- **Bucket C (theory, HONEST):** lemmas generalized to graded encoding + tuned weights (monotonicity +
  bounded-staleness corollary); Byzantine gate lemma tightened; **value-selection-not-robust Proposition**
  (matches the empirical null); committed-value safety theorem.
- **Bucket B (prob-gate):** Bayesian single-probability gate baseline — coded, τ-calibrated, grid re-run
  (BYTE-CONSISTENT: 0.0 diff on 552 existing cells, only 24 prob-gate cells added), figure, Methods, and
  the **honest** Results contrast ((T,I,F) is competitive-with but not-a-relabelling-of a calibrated
  scalar; value = selective abstention + frontier control + interpretable I/F separation).
- **Bucket D′ (emulated-WAN study):** Toxiproxy harness; **run + verified stable** (LAN/regional/WAN p50
  match across runs). `wan_latency.csv` (4 profiles × 3 patterns × n=800); figure f14; Results paragraph;
  Threats updated. Finding: tiers separate and the gap grows with latency (WAN fan-out p50 418 ms); under
  2% loss tails inflate to the 1 s deadline, worst for the fan-out (p99 1330 ms). Single-host emulation,
  not geo-distributed (stated).
- **Title:** "…in microservices architectures". **3v-iot-pg:** clone-and-go ready for Windows.

## RUNNING (auto-resume on completion)
- **Axis-B tune** (`bsg4bos64`, 4.5 h, 100% CPU): full-budget metaheuristic panel → `weight_tuning.csv`.
  The optimizer-agnostic finding is already smoke-validated; this is the rigorous confirmation. → tuning
  subsection + figure when it lands.

## REMAINING (then ns-dsl is submission-ready)
1. Integrate Axis-B subsection + figure (when tune lands).
2. **4th scenario** — ML feature-store / online-feature freshness (author-confirmed default; redirectable
   to IoT): add to `experiments/workload.py` + S4 calibration, re-run grid (byte-consistent + S4 added),
   integrate a generality result.
3. **SR-polish (A–G):** wlscirep template, restructure Intro→Results→Discussion→Methods, ≤8 display items
   + Supplementary, abstract ≤200 final, Nature refs/.bbl, cover letter, submission package.

## THEN (author-confirmed) → ns-microservices
Enrich-to-Q1 (modern selective-prediction baselines FIRST — conformal/MC-dropout/deep-ensembles/SR — then
datasets + deferral operator/score panel + MCAR/MAR/MNAR robustness + risk-coverage bounds) + SR
conversion. Experiments already validated; enrichment ADDS to a working base. Dedicated plan to be authored.

## Flagged for your sign-off (non-blocking)
LLM-use disclosure wording · 3 cover-letter reviewers · 4th-scenario domain (feature-store vs IoT).

## Resource discipline
8 cores (1 busy by the tune), 3.5 GiB RAM free. Heavy jobs staggered so the box never thrashes.
