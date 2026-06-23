# Cover letter — Scientific Reports

**DRAFT — author to review.** Items flagged `[CONFIRM]` need your sign-off before submission.

---

Dear Editors,

We submit our manuscript, **"A decentralized neutrosophic decision layer for global-state freshness in
microservices architectures,"** for consideration as an Article in *Scientific Reports*.

**The problem.** Microservices routinely make business decisions over *global* state — a price, a fraud
flag, a model feature — while each service is sovereign over its own data and the only cross-service
signal is a cache that may hold values that were never committed. The prevailing answer collapses this to
a boolean fresh/stale flag, which cannot distinguish a value held *only in cache* (unconfirmed) from one
that is genuinely stale or absent.

**The contribution.** We develop a decentralized decision layer in which each data item carries a
single-valued neutrosophic triple $(T,I,F)$ for its persistence status; peers fuse their views with
weighted operators and a deneutrosophy score and then *act or abstain* with no central authority. The
work is, to our knowledge, the first to turn this representation into a concrete, formally analysed, and
reproducibly evaluated mechanism. We provide one-round termination and safety/liveness guarantees
generalized to a graded encoding, a Byzantine analysis that separates gate robustness from
value selection (including a proven limitation and the precise fix it motivates), and a controlled
evaluation against strong, eventual, quorum, and single-probability baselines across four scenarios —
including a distinct ML feature-store domain — on a reproducible simulator plus a real, emulated-WAN
container testbed.

**Why *Scientific Reports*.** The work is a cross-disciplinary systems contribution: it bridges
neutrosophic decision theory, distributed-systems consistency, and reproducible empirical methodology,
and it is written to be accessible to a broad readership. We emphasise transparent, calibrated reporting —
every reported number regenerates end-to-end from committed code, a content-hashed calibration, and
recorded seeds — which we believe fits the journal's standards for rigour and openness. We make no
superiority claim over consensus protocols; we characterise a calibrated trade-off and report nulls
(e.g. that a calibrated single-probability gate is competitive) plainly.

**Statements.** This manuscript is original, is not under consideration elsewhere, and has not been
discussed with a member of the journal's editorial board prior to submission. The author declares no
competing interests and received no specific funding for this work.

`[CONFIRM]` **Suggested reviewers** (please confirm or replace — chosen for topical fit; verify no
conflicts of interest):
1. Rodrigo Laigner — data management in microservices (Online Marketplace benchmark).
2. Marko Vukolić — consistency in distributed storage; Byzantine fault tolerance.
3. Douglas B. Terry — consistency-based SLAs and freshness (Pileus).

`[CONFIRM]` **Opposed reviewers:** none / *(author to specify if any)*.

Thank you for considering our work.

Sincerely,
Haitham A. El-Ghareeb
Information Systems Department, Faculty of Computers and Information Sciences, Mansoura University,
Mansoura, Egypt — helghareeb@mans.edu.eg
