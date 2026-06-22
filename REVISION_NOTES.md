# ns-dsl — per-paper revision notes

Project-specific inputs for the 3-stage standing orders (PROJECT_BUILD_RULES → FIRST_REVISION →
REFERENCE_AUDIT → FINAL_REVISION). The cross-project order files are generic; this file holds what
is specific to the neutrosophic microservices decision-layer paper.

## State (2026-06-21)
Submission-track. Experiments **validated and reproducible on this laptop** (full chain re-ran →
canonical summaries byte-identical to the committed CSVs, 0 changes, same calibration hash
`fe4dcd…`; 74 tests green). Manuscript `paper/manuscript.tex` builds clean (19 pp, 0 undefined
cites/refs), full N5 order through Data/Code availability + references.

## Target venue (FINAL_REVISION Section 9)
**Scientific Reports / Nature Portfolio** (author decision 2026-06-21). The draft is currently
`elsarticle`; the final-revision pass converts it to Springer Nature **`sn-jnl`** (the same target
+ template as ns-hospital / edge-dq-ai / ns-fraud). Abstract ≤ ~200 words; Nature reference style.

## Author voice (Section 0.4 / 2.4)
**Keep the editorial "we"** (author decision 2026-06-21) — the draft already uses it (26 instances),
matching ns-hospital. Do NOT convert to single-author passive voice for this paper.

## Title fix (Section 1, at final revision)
Current title carries a colon and a subtitle:
"A Neutrosophic Decision Layer for Global-State Decisions in Microservices: A Reproducible
Evaluation of a (T,I,F)-Aggregating DSL and Rules Engine". Section 1.2 forbids colons and caps at
≤ 15 words. Revise to a colon-free ≤15-word title at the final stage — candidate to confirm with the
author: "A Neutrosophic Decision Layer for Global-State Decisions in Microservices" (10 words).

## What does NOT apply
- **Harf → Āthār rebrand (FINAL Section 10): NOT APPLICABLE** (no rename in flight).
- Neutrosophic spellings DO apply here (this paper is genuinely neutrosophic): keep "neutrosophic",
  "(T, I, F)", SVNN spelling consistent.

## Repository-deferral mode (FINAL Section 4.4)
ON. Data availability: the simulation is self-contained; the public code is "available to the editors
and peer reviewers on reasonable request from the corresponding author and will be released publicly
upon acceptance." No GitHub URL / script paths in the prose; remove the Code Availability section at
the final stage per the standing orders.

## Open scientific item (REFERENCE_AUDIT / before final)
- **El-Ghareeb 2019 (Neutrosophic Sets and Systems 25:136) operator forms.** `src/nsdsl/neutro/
  operators.py` implements standard SVNN weighted arithmetic/geometric aggregation (`svnnwaa`,
  `svnnwga`). Confirm these match the exact operator definitions in the author's NSS 25:136 paper
  before final submission; if NSS 25:136 uses a variant, either adopt it or cite the standard forms
  explicitly. **Needs the author's source paper to close.** Results are already STATUS:validated under
  the standard forms, so this is a citation/justification check, not a re-run.

## Suspect references to verify or remove (REFERENCE_AUDIT)
_(empty until the reference audit runs; each entry: `<bib_key> — <issue> — <verify|replace|remove>`)_
