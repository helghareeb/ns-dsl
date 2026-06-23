# ns-dsl review-response progress (updated 2026-06-23)

Venue = **Scientific Reports**. Manuscript: 34 pp elsarticle, builds clean (0 errors / 0 undefined refs),
every number validated + byte-consistent under one calibration hash (`16dc5ef…`). All committed to `main`.

## ✅ SCIENCE COMPLETE — every enrichment landed
- **Bucket A (presentation):** amsthm theorems; abstract 336→~205; `O(|R|)` complexity; graded-encoding
  anchor table; stats-accuracy fixes (5 seeds / 50 reps / 250 per cell / φ∈{0,0.1,0.2,0.3}; "300
  decisions" corrected from a stray 200); unit-of-analysis = per-repetition; pp effect sizes; full SHA-256;
  novelty-vs-2020 enumeration; threats expansion; future-work; keywords→6; 0 footnotes.
- **Bucket C (theory, HONEST):** graded-encoding generalization + bounded-staleness corollary; tightened
  Byzantine lemma; **value-selection-not-robust proposition**; committed-value safety theorem.
- **Bucket B (prob-gate):** Bayesian single-probability baseline; byte-consistent grid; figure; the honest
  "(T,I,F) is competitive-with but not-a-relabelling-of a calibrated scalar" framing.
- **Bucket D′ (emulated-WAN):** Toxiproxy tail-latency study, **verified stable**; figure f14 + Results +
  Threats. Tiers grow with latency; loss inflates tails to the deadline (fan-out worst).
- **Operator panel (Axis A), Score panel (Axis A′), Byzantine null, Scalability** — all integrated.
- **Axis-B tuning:** full 7-optimizer × 3-scenario panel; honest finding — tuning beats uniform only under
  asymmetric cost (S2 +10.1%; S1/S3 +0%), optimizer-agnostic (No Free Lunch). Figure f15.
- **S4 cross-domain generality:** ML feature-store scenario added (byte-consistent: S1/S2/S3 identical,
  192 S4 cells added); Pareto interior replicates; honestly labeled stylized (not real traces).
- **Reference audit:** removed 1 suspect uncited ref; verified cited recent refs real + upgraded to
  published venues/DOIs (RALF, Online-Marketplace SIGMOD'25, GoldFish IoT'24, RIME). 44 entries, 0 undefined.

## ✅ PROSE LINE-EDIT — two reviewers + de-chapter (2026-06-23, commit 316599c)
Language/presentation pass on author's two friend-reviews (Information Sciences, "minor revision:
language"). **Prose-only, proven**: build clean 33 pp, 0 errors / 0 undefined; result-number multiset,
all citation keys, and all 39 `\label` defs **IDENTICAL to pre-edit HEAD** (R1 integrity).
- **De-chapter** (author directive, primary): deleted the "What the 2020 sketch settled…" and "For an
  honest delineation" paragraphs; intro now cites the chapter once, neutrally; Methods (0,0,1) note
  reworded without "sketch" narrative. `elghareeb2020neutro` prose cites 5 → 2; paper stands alone.
- **Grammar**: abstract fragment fixed; "the axis a bit discards is indeterminacy" fixed.
- **De-compress**: abstract proof sentence + Contributions item 5 split.
- **Diction**: apples-to-apples → directly comparable; "collapses a decisive distinction" → "two
  qualitatively different states"; "panel is separable" → "operators differentiate"; "against a single
  hop" → "compared to"; precise super-linear wording; dropped "earns its keep"/"tellingly"/"direction
  that matters"; rhetorical "honest" ×4 removed (6 left are technical Byzantine terms); cover letter matched.
- **Accessibility**: neutro-waa + SVNNWAA/SVNNWGA spelled out at first Results use; "deneutrosophy score"
  glossed; "Why now." → "Contemporary relevance."; artifact → artefact throughout; thinned `\emph`.
- **Flagged for author**: LLM-use disclosure wording must name the model.
- **Deferred to SR-formatting pass**: elsarticle `\paragraph{Title.}` renders a double period
  ("Contributions.."); fix when headings are reworked for wlscirep (systemic, pre-existing).

## ▶ REMAINING — SR-polish (well-defined; plan sections A–G)
The manuscript is submittable to SR as a PDF in substance; remaining items are venue formatting + packaging:
1. **wlscirep template** (optional but recommended): download `wlscirep.cls`; port into `paper/submission/`.
2. **Restructure to SR order:** Intro → Results (subheadings) → Discussion (fold Threats + Conclusion) →
   **Methods last**. (The big surgery — best done as a focused pass.)
3. **≤8 main display items:** curate the ~12 figures + tables to the 8 headline ones; rest → Supplementary.
4. **Refs → Nature numeric style + `.bbl`**; add DOIs to the remaining classic entries (dombi, aczel,
   wolpert NFL, storn DE, kennedy PSO, hansen CMA-ES — all real, need verified DOIs).
5. **Cover letter** + **submission package** (single PDF ≤3 MB + figures + SI).
6. Final exact abstract ≤200 with the editor word tool.

## THEN → ns-microservices (author-confirmed)
Enrich-to-Q1 (modern selective-prediction baselines FIRST) + SR. Experiments already validated.

## Flagged for sign-off (non-blocking)
LLM-use disclosure wording · 3 cover-letter reviewers · 4th-scenario domain (feature-store default kept).
