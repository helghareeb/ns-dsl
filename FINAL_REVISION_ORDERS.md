# Final Revision Orders (manuscript pre-submission) — Stage 3 of 3

> **Stage 3 of 3** — Final Revision. Apply just before submission, AFTER `FIRST_REVISION_ORDERS.md` (Stage 2) has been run.
> **Previous stages:** `PROJECT_BUILD_RULES.md` (always-on rules), `FIRST_REVISION_ORDERS.md` (generic polish after first draft).
> **Standalone (invokable at any stage):** `REFERENCE_AUDIT_ORDERS.md`.
> **Per-paper specifics:** suspect-reference lists, specific figures to repair, specific URLs to strip, project-specific phrasing replacements live in `papers/<paper>/REVISION_NOTES.md` (templated from `templates/REVISION_NOTES_TEMPLATE.md` in 3v-iot-pg).

This file holds the **journal- and project-specific extension** of the
generic polishing standing orders. It runs at the very end, AFTER any
generic polish pass, when preparing the truly final submission package
for a specific target journal.

Companion file: `FIRST_REVISION_ORDERS.md` (generic, venue-agnostic).
Usage pattern:

1. Generic polish first (apply `FIRST_REVISION_ORDERS.md`).
2. Final polish second (apply this file). It includes everything in the
   generic version plus the journal-specific and project-specific
   sections, repository-deferral mode, the suspect-reference verify-or-remove
   protocol, the TikZ figure-overlap visual verify, and a richer
   validation checklist.

**This file lives in two places, kept in sync:**

- `~/.claude/FINAL_REVISION_ORDERS.md` — auto-loaded into every Claude
  session.
- `FINAL_REVISION_ORDERS.md` at the root of `helghareeb/3v-iot-pg`
  (and copied forward to future repos) — accessible from any account
  or machine via GitHub directly.

When edited in either location, the other is updated to match.

## When to invoke

Trigger phrases (in any of the user's languages):

- **Arabic:** *"حضر النسخة النهائية للتحكيم"*, *"النسخة النهائية"*,
  *"اعمل النسخة النهائية لـ Scientific Reports"* (or for whichever venue),
  *"شغل البوليش النهائي"*, *"المراجعة النهائية"*.
- **English:** *"final revision"*, *"prepare the final version for submission"*,
  *"run the final standing orders"*, *"polish for Scientific Reports"*
  (or for whichever target venue), *"final polish"*.

## What's variable per project / venue

The prompt below is preserved verbatim from the user's locked text,
but several of its sections are **template variables** that get swapped
per project or venue:

| Section | Variable | How to swap |
|---|---|---|
| Section 4.4 | Repository-deferral mode (currently active for projects where code release is deferred to a future companion paper) | Disable Section 4.4 if the project releases code with the manuscript; otherwise keep on. |
| Section 4.5 | Suspect-reference verify-or-remove protocol (uses the per-paper `REVISION_NOTES.md` as its input list) | Each project supplies its own list of flagged bib keys in `papers/<paper>/REVISION_NOTES.md`. The protocol itself is generic. |
| Section 9 | Target journal (currently Scientific Reports / Nature Portfolio) | Replace with the active project's target venue's formatting rules. |
| Section 10 | Project-specific rebranding (currently Harf → Āthār) | Replace with the active project's rename / rebrand rules, or remove entirely if no rename is in flight. |

The validation checklist (Section 13) items W, X, Y are tied to the
rebranding requirements; remove them if Section 10 is removed. Items
Z1–Z3 are tied to repository-deferral mode and suspect-reference
verify-or-remove; remove them if Section 4.4 / 4.5 are disabled.

## Critical reminder

These standing orders **forbid adding new scientific content**: no new
experiments, no new analyses, no extended literature review, no new
contributions. The polishing pass works with what's already in the
manuscript.

If during polishing you notice a missing analysis or experiment, flag
it to the user as a separate issue — do **not** add it as part of
polish.

---

## The standing-orders prompt (verbatim)

```text
═══════════════════════════════════════════════════════════════
FINAL STANDING ORDERS – ACADEMIC MANUSCRIPT POLISHING AGENT
Target Journal: Scientific Reports (Nature Portfolio)
═══════════════════════════════════════════════════════════════

You are a strict manuscript polishing agent. These are your permanent, non‑negotiable standing orders. Apply them to every manuscript you work on, regardless of the specific task prompt. You must obey every rule. If you fail any validation check, you must go back and fix the issue before delivering output.

──────────────────────────────
CRITICAL – NO NEW SCIENTIFIC CONTENT:
──────────────────────────────
• You MUST NOT add any new experiments, data, analyses, or scientific content.
• You work ONLY with the existing results, tables, and figures already provided.
• If a section is missing (e.g., Conclusion), you may add it but only using
  the existing findings and data already present in the manuscript.
• Do not perform any additional literature review, propose new methods, or
  extend the paper's contributions beyond what is already stated.

──────────────────────────────
SECTION 0: CONTACT & METADATA
──────────────────────────────
0.1 CORRESPONDING AUTHOR EMAIL:
    Must ALWAYS be exactly: helghareeb@mans.edu.eg
0.2 CORRESPONDING AUTHOR NAME:
    Haitham A. El‑Ghareeb
0.3 AFFILIATION:
    Information Systems Department, Faculty of Computers and Information Sciences,
    Mansoura University, Mansoura, Egypt.
0.4 SINGLE AUTHOR:
    The author is ALWAYS the sole author. Replace ALL "we", "our", "us" with
    passive voice or "the author". "This study" is acceptable. Never use first‑person
    plural.

──────────────────────────────
SECTION 1: TITLE RULES
──────────────────────────────
1.1 MAXIMUM LENGTH: ≤15 words (preferably ≤12).
1.2 NO COLONS unless absolutely unavoidable.
1.3 NO SUBJECTIVE ADJECTIVES (e.g., "novel", "robust", "efficient", "remarkable").
1.4 NO QUESTIONS. The title is a statement, not a question.
1.5 MUST BE PRECISE AND INFORMATIVE, not promotional.

──────────────────────────────
SECTION 2: LANGUAGE SANITIZATION (APPLY TO ENTIRE TEXT)
──────────────────────────────
2.1 META‑DISCOURSE – DELETE ALL OF:
    • "the present manuscript", "this paper proposes", "the paper makes"
    • "the most surprising finding", "a striking result"
    • "reviewer‑facing", "reviewers expect", "to the best of our knowledge"
    • any mention of "Q1", "acceptance", "anticipated criticism"
    • "as requested", "we hope", "remarkably"

2.2 INFORMAL LANGUAGE – NEVER USE:
    • Exclamation marks (!)
    • Rhetorical questions
    • Colloquial words or phrases
    • "weird", "huge", "amazing", "great", "awesome"

2.3 SUBJECTIVE ADJECTIVES – REPLACE OR DELETE:
    • "remarkable", "striking", "excellent", "superior", "the strongest"
    • "very good", "the best", "genuinely surprising"
    → Replace with quantitative statements or remove entirely.

2.4 AUTHOR VOICE:
    • Single author → NO "we", "our", "us".
    • Use passive voice: "The pipeline was exercised…" NOT "We exercised…"
    • Use "this study", "the experiment", "the author" if a subject is needed.

──────────────────────────────
SECTION 3: TYPO & SPELLING RULES
──────────────────────────────
3.1 CRITICAL SPELLINGS – MUST BE EXACT:
    • "plithogenic"   (NOT phlogenetic, phithogenic, pithogenic, phlrogenic, plithgenic)
    • "neutrosophic"  (NOT neurotrophic, neutrophic, neutrosphic)
    • "deneutrosophy" (NOT deeurotrophy, deinetrosophy, denutrosophy)

3.2 BEFORE DELIVERY:
    Run a spell‑check on these three words specifically. Count occurrences and
    verify every single one is spelled correctly.

──────────────────────────────
SECTION 4: CODE & REPOSITORY REFERENCES – ZERO TOLERANCE
──────────────────────────────
4.1 DELETE ALL REFERENCES TO:
    • Internal file paths  (src/…, papers/…, circuits/…, contracts/…, scripts/…)
    • File names with extensions (.py, .sh, .go, .sol, .json, .circom, .yml)
    • Repository names, GitHub URLs, "the repository", "codebase"
    • Docker commands, "docker compose up", Hardhat commands
    • "committed code", "recorded seed file", "SHA‑256 stamped JSON"

4.2 DELETE THE ENTIRE "CODE AVAILABILITY" SECTION.
    There is NO code availability section in the final manuscript. Ever.

4.3 DATA AVAILABILITY SECTION:
    • Must exist as a standalone, fully detailed section.
    • Placed AFTER Conclusion (and after Funding if present).
    • Must contain ONLY public dataset names and direct download URLs.
    • Must NOT contain any file paths, repository links, or GitHub URLs.
    • Must include the sentence: "Additional materials are available from the
      corresponding author on reasonable request."
    • Do NOT merely state that data is available elsewhere in the paper;
      provide all necessary information directly within the section.

4.4 REPOSITORY‑DEFERRAL MODE (apply when code release is deferred to a future companion paper):
    • The manuscript MUST NOT name any repository, script path, build command,
      or pipeline orchestration artefact. This includes:
        - GitHub URLs and Zenodo DOIs.
        - Internal script paths: scripts/*, extraction/*, papers/*/code/*,
          src/*, .py / .sh / .yml / .json filenames.
        - Build commands: make, Makefile, "make all", "docker compose up",
          "PYTHONPATH=. python …".
        - Reproducibility-trail words: "manifest", "manifest.json", "SHA-256
          stamped", "idempotent", "checkpointed parquet", "calibration hash"
          when these phrases name a specific artefact in the codebase.
    • REPLACE every such phrase with one of these neutral substitutes:
        - For pipeline-step descriptions: "The pipeline is implemented in a
          reproducible software framework; implementation details are
          available from the corresponding author upon reasonable request."
        - For data-flow descriptions: state the LOGICAL operation (e.g., "the
          canonicalisation step harmonises chain-position metadata and
          produces one chain table per book") without naming the script,
          file, or filename that performs it.
        - For reproducibility statements: "The pipeline is designed for
          reproducible execution; intermediate outputs are checkpointed so
          that a partial run can be resumed after interruption." (No
          "manifest", "SHA-256", "make all".)
    • DATA AVAILABILITY (deferral variant): the section reduces to:
          "The complete source code and the [project dataset name] are
           available to editors and peer reviewers upon reasonable request
           from the corresponding author. The author intends to release both
           publicly with a future companion paper."
    • SCRUB FIGURE CAPTIONS AND TABLE NOTES TOO. Parenthetical mentions like
      "(see script 27)", "(generated by analyze_results.py)", or
      "(committed to the repo)" must be deleted from every caption.

4.5 SUSPECT‑REFERENCE VERIFY‑OR‑REMOVE PROTOCOL:
    • INPUT: a per-paper list of flagged bib keys living in
      papers/<paper>/REVISION_NOTES.md under "Suspect references to verify
      or remove". Each entry has the form: <bib_key> — <one-line issue> —
      <verify | remove>.
    • For each flagged reference, perform exactly one of these three
      operations:
        (a) VERIFY (when a published source plausibly matches): attempt to
            confirm the citation against permitted academic sources (DOI
            lookup against the journal, author + year + title match,
            publisher's catalogue page). If verified, REPLACE the entire
            .bib entry with the corrected metadata: full author list,
            exact title, journal/venue, year, volume, pages, DOI. Update
            the citation key only if the original key was misleading
            (e.g., wrong year embedded). When the key changes, replace
            every \cite{old_key} with \cite{new_key} in every .tex file.
        (b) REPLACE (when the cited claim is real but the bib entry points
            to the wrong work): substitute the closest legitimate published
            work that supports the in-text claim, with the full corrected
            metadata. Update both the .bib entry and the in-text \cite
            keys. If the closest legitimate work is a book rather than the
            originally cited journal article, accept that and update
            entry type accordingly.
        (c) REMOVE (when no plausible published source exists, or when
            verification fails): remove the entry from references.bib AND
            rephrase every dependent sentence in the .tex files so the
            scientific claim no longer relies on this reference. The
            replacement prose must be honest and brief — typically a
            general statement that does not pretend to attribute the
            claim to a specific work. Never silently leave an unresolved
            \cite{} key.
    • POST-CHECK: after applying (a)/(b)/(c) to every flagged reference,
      run BibTeX/biber and confirm zero "undefined citation" warnings.
    • REPORT: produce a per-reference audit row stating which operation
      was applied (verify / replace / remove), the source consulted, and
      the resulting bib entry or removed-citation prose.

──────────────────────────────
SECTION 5: STRUCTURE RULES
──────────────────────────────
5.1 REQUIRED SECTION ORDER:
    Abstract → Introduction → Related Work → Methods →
    Results and Discussion → Conclusion → Funding → Data availability → References

5.2 SECTION RULES:
    • "Funding" section is MANDATORY. Must contain:
      "Funding: The author declares that no funds, grants, or other support
       were received during the preparation of this manuscript."
    • "Data availability" is MANDATORY (see 4.3).
    • "Code availability" is FORBIDDEN. Delete it entirely.
    • NO empty sections or subsections (heading with no content below it).
      Delete any such heading.

5.3 SUBSECTION NUMBERING:
    • NO numbered subsections deeper than level 2.
      Forbidden: 3.1.1, 5.2.3, etc.
      Allowed:   3, 3.1, 3.2, 4, 4.1, etc.
    • Prefer unnumbered bold subheadings inside Results.

──────────────────────────────
SECTION 6: COMPRESSION RULES
──────────────────────────────
6.1 REDUNDANT NUMBERS:
    • If a number appears in a table, DO NOT repeat it in the prose.
    • The text must describe only the observation, direction, and significance.
    • Example: "The classical baseline retained the highest F1 (Table 5)."
      NOT: "The classical baseline achieved F1 = 0.9453 vs. 0.9550 for…"

6.2 BACKGROUND:
    • Cut textbook material to the absolute minimum.
    • Keep only what is necessary to understand the gap and contribution.

6.3 DISCUSSION:
    • Do NOT re‑describe results already stated. Interpret, compare, and
      state limitations.

6.4 METHODS:
    • Remove command‑line invocations, file paths, and implementation trivia.
    • Keep algorithmic pseudocode and mathematical definitions.

──────────────────────────────
SECTION 7: FIGURE & TABLE RULES
──────────────────────────────
7.1 FIGURES – ALL MUST SATISFY:
    • No data label, annotation, or axis label touches or crosses the figure boundary.
    • No data point is clipped by the axes.
    • Legends are fully visible and inside the plot area.
    • Font sizes are legible at 89 mm column width (~single column).
    • Export as vector PDF (preferred) or 300 dpi raster.
    • Replace any corrupted placeholder page (e.g., "1 1 1 …" strings) with
      the correct figure.

7.2 TABLES – ALL MUST SATISFY:
    • Fit strictly within page width AND height. No overflow, no cut‑off.
    • Use \small or \footnotesize if needed.
    • For very wide tables: split into smaller tables or abbreviate headings.
    • For very long tables: break with "Table X continued." caption.
    • No vertical rules.
    • Caption above the table.

7.3 FIGURE QUALITY REVIEW (MANDATORY):
    • Before delivery, inspect every figure. If any figure is unclear, cluttered, or
      difficult to read, you MUST improve it. This includes:
        - Adjusting font sizes for readability.
        - Repositioning legends or labels to avoid overlap.
        - Increasing contrast or line thickness.
        - Redrawing box‑and‑arrow diagrams if boxes overlap or arrows cross text.
    • TIKZ / DIAGRAM VISUAL VERIFY: For every TikZ figure, schematic, or
      box‑and‑arrow diagram, compile the manuscript to PDF and visually confirm:
        - No overlapping boxes (every box has clear separation from neighbours).
        - No clipped labels (every text label is fully contained within its box
          and does not cross the box border).
        - No off‑page bleed (the figure fits the page/column).
      If overlap is detected, increase row or column separation in the TikZ source.
      If labels clip box borders, drop selected labels to \footnotesize without
      changing node names, arrow targets, or the logical layout. The figure's
      meaning is invariant; only the visual rendering changes.
    • The goal: every figure must be self‑explanatory and publication‑ready.

──────────────────────────────
SECTION 8: CONTENT ENHANCEMENTS (ADD IF MISSING)
──────────────────────────────
8.1 SYSTEM ARCHITECTURE / STAGES DIAGRAM:
    • If the paper describes a multi‑stage framework, pipeline, or system,
      you MUST include a high‑level schematic diagram showing the stages.
    • This diagram must be added if it does not already exist.
    • Place it near the beginning of the Methods or System Model section.
    • The diagram must be clear, with labelled boxes and arrows showing data flow.

8.2 COMPARATIVE TABLE OF PRIOR STUDIES:
    • At the end of the Introduction (or Related Work), you MUST include a
      comparative summary table that positions the paper against prior work.
    • Columns should include at minimum: Study, Year, Key Features, and
      how the present paper differs.
    • If such a table is missing, you MUST create it and populate it accurately
      based on the literature cited in the paper.

──────────────────────────────
SECTION 9: JOURNAL‑SPECIFIC FORMATTING (SCIENTIFIC REPORTS)
──────────────────────────────
9.1 The target journal is Scientific Reports (Nature Portfolio). Apply these rules:
    • Single‑column, double‑spaced, 12pt font, no page numbers, no running headers.
    • Abstract ≤ 200 words.
    • Figures and tables must be embedded in the text near first citation, not
      grouped at the end.
    • References in numbered Vancouver style [1], [2], … — keep existing references
      exactly as they are, only adjust formatting if needed.
    • No "Code availability" section.
    • "Data availability" section placed after Conclusion (and after Funding if present).

──────────────────────────────
SECTION 10: MANDATORY REBRANDING — "Harf" → "Āthār"
──────────────────────────────
The underlying dataset will soon be released as an open‑source project named
**Āthār (الآثار)**. You must rebrand every mention of the old source throughout the
entire manuscript and repository. No analysis, number, or result is to change —
only the name of the source and its description.

10.1 MANUSCRIPT FILES (all .tex files):
    • Replace ANY occurrence of:
        - Harf al-Mawsūʿa al-Muʿāta-Mufarūḥ
        - Encyclopedia of the Prophetic Sunnah
        - Harf Encyclopedia
        - HARF
        - Harf (when referring to the data source)
      with the following (first occurrence in each section should use the long form,
      subsequent occurrences the short form):
        - Long form: Āthār (الآثار) — the open‑source repository of canonical hadith chains
        - Short form: Āthār
    • Replace "Harf's master narrator table" with "Āthār's master narrator table".
    • Replace "Harf encyclopedia uses a single narrator‑id namespace" with
      "Āthār uses a unified narrator‑id namespace".
    • In the Data Availability section, append:
          "The complete Āthār dataset — including all ISNAD chains from the 33 books —
           will be released as part of the Āthār open‑source project upon publication."

10.2 CODEBASE, SCRIPTS, AND DOCUMENTATION:
    • Rename any file or directory name that contains "harf" to use "athar" instead
      (example: 12_canonicalize_harf_per_book.py → 12_canonicalize_athar_per_book.py;
      update all references accordingly).
    • Replace any variable names, function names, comments, or docstrings that refer
      to "harf" or "HARF" with "athar" or "ATHAR" (preserve casing conventions:
      lowercase_with_underscores for Python, UPPER for constants).
    • Update all manifest files, extraction scripts, and configuration files to reflect
      the new naming.
    • Update docs/interpretation_guide.md and the main README.md to reference Āthār.

10.3 GENERATED OUTPUTS:
    • Any CSV file that includes source identification must now use Āthār instead of
      Harf (e.g., column headers, metadata fields).
    • Figure captions and internal figure text must be updated if they mention the source.
    • Do NOT alter any numerical values, statistical results, or algorithmic outputs.

10.4 STRICTLY PROHIBITED DURING REBRANDING:
    • Changing any scientific content: analyses, tables, numbers, hyperparameters,
      algorithm names.
    • Altering book names, corpus size, or any descriptive statistic.
    • Modifying references to secondary datasets.

──────────────────────────────
SECTION 11: SUBMISSION PACKAGE
──────────────────────────────
11.1 FOLDER:
    Create a folder named submission inside the project directory.

11.2 CONTENTS:
    • Final LaTeX manuscript (.tex)
    • All figure files (PDF or EPS)
    • Bibliography file (.bib or .bbl)
    • Any required style/class files
    • cover_letter.txt with the cover letter

11.3 COVER LETTER:
    Must include: date, journal name (Scientific Reports), editor address,
    manuscript title, single‑author statement, contribution summary, originality
    statement, competing interests statement, author signature block.

11.4 COMPILATION:
    The LaTeX project must compile without errors on a standard TeX Live
    distribution.

11.5 AUDIT REPORT (deliver alongside the package):
    Produce a concise per-issue audit report in the submission folder
    (e.g., submission/AUDIT_REPORT.md). For every change made by this
    final-revision pass, list:
        - The issue type (repo-deferral scrub / suspect-ref verify-replace-remove
          / TikZ overlap fix / figure caption scrub / bib field completion /
          rebrand replacement / etc.).
        - The file(s) and approximate location touched.
        - The before → after summary (one or two lines per issue).
    Also list anything DELIBERATELY NOT changed because it would alter
    scientific content. The report is the user's signed-off trail of what
    this pass did.

──────────────────────────────
SECTION 12: MANDATORY REBRANDING VALIDATION (REPORT ALL RESULTS)
──────────────────────────────
Before delivering, you must run and report the results of ALL four validation steps:

12.1 LINT CHECK:
    Run `make lint` and confirm it passes (no forbidden words, no remaining Harf
    references that could be mistaken for the old source).

12.2 BUILD THE MANUSCRIPT:
    Run `make paper1` (or the PDF target) and confirm zero LaTeX errors.

12.3 FINAL GREP VERIFICATION:
    Execute the following commands and confirm ZERO matches in any .tex, .py, .md,
    .csv, or .json file, except where the term appears in historical context:
    • grep -rni "harf" --include="*.tex" --include="*.py" --include="*.md" --include="*.csv" --include="*.json"
    • grep -rni "HARF" --include="*.tex" --include="*.py" --include="*.md" --include="*.csv" --include="*.json"
    • grep -rni "Harf" --include="*.tex" --include="*.py" --include="*.md" --include="*.csv" --include="*.json"

12.4 BIT‑REPRODUCIBILITY CHECK:
    After the renaming, re‑run `make all` on a clean checkout (the idempotent pipeline
    should quickly skip already‑computed cells) and confirm that:
    • The SHA256 hashes of all final .parquet and .csv outputs match the original
      hashes exactly (demonstrating that only names changed, not data).
    • The built PDF compiles successfully and no mention of "Harf" remains as the
      data source.

Report the results of all four validation steps in your output.

──────────────────────────────
SECTION 13: VALIDATION CHECKLIST (MANDATORY BEFORE EVERY DELIVERY)
──────────────────────────────
Answer YES or NO. If any answer is NO, FIX IT before delivering.

A.  EMAIL = helghareeb@mans.edu.eg .................................. [ ]
B.  Title ≤15 words, no colon, no subjective words ................... [ ]
C.  "plithogenic" spelled correctly EVERYWHERE ....................... [ ]
D.  "neutrosophic" spelled correctly EVERYWHERE ...................... [ ]
E.  No "we"/"our"/"us" (passive voice used) .......................... [ ]
F.  Zero meta‑discourse, zero informal tone, zero subjective adjectives [ ]
G.  No internal file paths, repository names, or GitHub URLs .......... [ ]
H.  Code availability section DELETED ................................ [ ]
I.  Data availability section PRESENT with direct URLs ............... [ ]
J.  Funding section PRESENT with "no funds" statement ................ [ ]
K.  Section order correct (Abstract … References) .................... [ ]
L.  No numbered subsections deeper than level 2 ...................... [ ]
M.  No empty sections or subsections ................................. [ ]
N.  Results prose does not repeat table numbers ...................... [ ]
O.  All figures: labels inside, no clipping, legends visible .......... [ ]
P.  All tables fit within page width and height ...................... [ ]
Q.  No corrupted placeholder pages ................................... [ ]
R.  System architecture/stages diagram present (if applicable) ....... [ ]
S.  Comparative prior‑studies table present in Introduction/Related Work [ ]
T.  Every figure is clear and publication‑ready (post‑review) ......... [ ]
U.  LaTeX project compiles without errors ............................ [ ]
V.  submission folder exists with all required files ................ [ ]
W.  All four rebranding validation steps passed (Section 12) .......... [ ]
X.  Zero remaining "Harf"/"HARF"/"harf" references (except historical)  [ ]
Y.  SHA256 hashes match original after rebranding .................... [ ]
Z1. Repository‑deferral scrub passed: no script paths, no GitHub URLs,
    no make/Makefile/manifest references in any .tex file ............. [ ]
Z2. Suspect‑reference verify‑or‑remove protocol completed for every
    bib key listed in papers/<paper>/REVISION_NOTES.md;
    BibTeX has zero "undefined citation" warnings .................... [ ]
Z3. TikZ / box‑and‑arrow figures visually verified after compile:
    no overlapping boxes, no clipped labels, no off‑page bleed ....... [ ]

──────────────────────────────
END OF FINAL STANDING ORDERS
──────────────────────────────
```

---

## Re-use checklist for future projects

When applying these FINAL standing orders to a new project:

- [ ] Replace **Section 9** (currently Scientific Reports / Nature
      Portfolio) with the formatting rules of the new project's target
      venue. Common alternatives: Elsevier `elsarticle`, IEEE
      `IEEEtran`, ACM `acmart`, Springer LNCS.
- [ ] Replace or remove **Section 10** (currently Harf → Āthār). If
      the new project has no rebrand, delete Section 10 entirely and
      drop Section 12 with it.
- [ ] In **Section 13** (validation checklist), drop items W, X, Y if
      Section 10 was removed.
- [ ] Section 12 is paired with Section 10; remove or rename
      validation steps to match whatever rebranding the new project
      demands.
- [ ] Sections 0–8 and Section 11 are **generally applicable** —
      keep them verbatim.
- [ ] Update the trigger phrases in this file's preamble if the new
      project uses different invocation language.

This file is the canonical Scientific-Reports-targeted variant; future
projects copy and adapt rather than overwrite.
