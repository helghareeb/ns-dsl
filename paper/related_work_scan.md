# Related Work Literature Scan

**Target venue:** Future Generation Computer Systems (Elsevier, Q1)
**Paper topic:** A decentralized neutrosophic (T, I, F) decision/consistency layer for
global-state decisions in microservices. Each data item carries a single-valued
neutrosophic triple for its persistence status (persisted / cached / absent); peer
microservices fuse their views using SVNNWAA / SVNNWGA aggregation operators plus a
deneutrosophy score function to decide whether a cached value is fresh / consistent
enough to act on, with no central authority. It is a freshness/consistency **decision
layer** that sits **above** the consistency substrate (it is NOT a replication/consensus
protocol). Includes a JSON DSL + ANTLR-parsed rules engine. Evaluated on an e-Commerce
testbed against centralized, quorum-of-booleans, Raft-LWW, CRDT/LWW, and naive-cache
baselines.

**Extends:** El-Ghareeb (2020), Elsevier book chapter,
DOI `10.1016/B978-0-12-819670-0.00002-0` — conceptual proposal, no implementation or
experiments.

**Scan date:** 2026-06-15. Searches favored 2021–2026 with seminal older works retained.
Items marked "(verify)" need a final detail check during the reference-audit pass
(per `REFERENCE_AUDIT_ORDERS.md`).

---

## Bucket 1 — Microservices state management & data consistency

Saga, event sourcing, eventual consistency in microservices, BAC theorem, data
sovereignty. This is the substrate our layer sits above; we cite it to frame the problem
(per-service data ownership, decentralized state, no global transaction).

- **Pardon, Pautasso & Zimmermann (2018)** — *Consistent Disaster Recovery for
  Microservices: the BAC Theorem.* IEEE Cloud Computing 5(1), 49–59.
  DOI `10.1109/MCC.2018.011791714`.
  Relevance: the BAC (Backup–Availability–Consistency) impossibility result for
  whole-application microservice state — direct theoretical framing for "you cannot get
  a globally consistent view of decentralized state for free."

- **Di Francesco, Lago & Malavolta (2019)** — *Architecting with microservices: A
  systematic mapping study.* Journal of Systems and Software 150, 77–97.
  DOI `10.1016/j.jss.2019.01.001`.
  Relevance: Q1 (JSS) mapping study that identifies data management / consistency as a
  top open challenge in microservice architecture — motivates the gap.

- **Soldani, Tamburri & van den Heuvel (2018)** — *The pains and gains of microservices:
  A systematic grey literature review.* Journal of Systems and Software 146, 215–232.
  DOI `10.1016/j.jss.2018.09.082`.
  Relevance: industrial evidence that distributed-data consistency and state management
  are recurring "pains"; a 2024 follow-up ("revisited", PROFES 2024) tracks how these
  pains evolved (verify exact 2024 citation).

- **Laigner, Zhou, Salles, Liu & Kalinowski (2021)** — *Data management in microservices:
  State of the practice, challenges, and research directions.* Proceedings of the VLDB
  Endowment (PVLDB) 14(13), 3348–3361. DOI `10.14778/3484224.3484232`.
  Relevance: VLDB Q1 study explicitly on data management in microservices; documents how
  practitioners handle replicated/cached cross-service data and the consistency
  workarounds they adopt — strong direct anchor for our problem statement.

- **Štefanko, Chaloupka & Rossi (2019)** — *The Saga Pattern in a Reactive Microservices
  Environment.* Proc. ICSOFT 2019, 483–490. DOI `10.5220/0007918704830490` (verify).
  Relevance: representative treatment of the saga pattern (compensation-based eventual
  consistency) — a key baseline mechanism class our layer is orthogonal to.

- **Richardson (2018)** — *Microservices Patterns: With Examples in Java.* Manning.
  ISBN 9781617294549.
  Relevance: canonical catalog of Saga, Event Sourcing, CQRS, and Database-per-Service —
  cite for the "data sovereignty / per-service database" premise our triple encodes.

- **Newman (2021)** — *Building Microservices, 2nd ed.* O'Reilly. ISBN 9781492034025.
  Relevance: widely cited reference for decentralized data ownership and the rejection of
  a shared central datastore — supports the "no central authority" design goal.

- **Laigner, Kalinowski, Lifschitz, Monteiro & de Oliveira (2020)** — *A systematic
  mapping of software engineering challenges for microservice architectures.* (verify
  venue/DOI; possibly SAC/ICEIS). Relevance: secondary mapping reinforcing data
  consistency as an under-tooled challenge.

---

## Bucket 2 — CRDTs & bounded staleness / causal consistency

Consistency models and convergent data types. CRDT/LWW is one of our baselines; bounded
staleness and causal+ are the formal vocabulary we use to describe what "fresh enough"
means.

- **Shapiro, Preguiça, Baquero & Zawirski (2011)** — *Conflict-Free Replicated Data
  Types.* Proc. SSS 2011, LNCS 6976, 386–400. DOI `10.1007/978-3-642-24550-3_29`.
  (Companion INRIA RR-7687, "A comprehensive study of Convergent and Commutative
  Replicated Data Types.")
  Relevance: foundational CRDT formalization; LWW-Register/LWW-Element-Set is the CRDT/LWW
  baseline we compare against.

- **Preguiça (2018)** — *Conflict-free Replicated Data Types: An Overview.* arXiv
  1806.10254 (also Springer ESBD chapter version).
  Relevance: accessible CRDT survey for the state- vs op-based taxonomy and convergence
  guarantees; positions CRDTs as "convergence, not freshness-of-decision."

- **Lloyd, Freedman, Kaminsky & Andersen (2011)** — *Don't settle for eventual: Scalable
  causal consistency for wide-area storage with COPS.* Proc. SOSP 2011, 401–416.
  DOI `10.1145/2043556.2043593`.
  Relevance: defines causal+ consistency as the strongest model achievable with
  always-available low-latency operations — the consistency ceiling our decision layer
  operates beneath/above.

- **Bailis, Venkataraman, Franklin, Hellerstein & Stoica (2012/2014)** —
  *Probabilistically Bounded Staleness for Practical Partial Quorums.* PVLDB 5(8),
  776–787. DOI `10.14778/2212351.2212359`. (Extended: VLDB Journal 2014,
  DOI `10.1007/s00778-013-0330-1`.)
  Relevance: PBS quantifies how stale a quorum read is likely to be — the closest prior
  art to "probabilistic freshness of a cached value," but boolean/quorum-based, not a
  T/I/F decision.

- **Abadi (2012)** — *Consistency Tradeoffs in Modern Distributed Database System Design:
  CAP is Only Part of the Story* (PACELC). IEEE Computer 45(2), 37–42.
  DOI `10.1109/MC.2012.33`.
  Relevance: PACELC's else-latency-vs-consistency tradeoff is the design tension our
  layer manages explicitly per data item; frame the contribution as a tunable point on
  the L/C spectrum.

- **Brewer (2012)** — *CAP twelve years later: How the "rules" have changed.* IEEE
  Computer 45(2), 23–29. DOI `10.1109/MC.2012.37`.
  Relevance: the consistency/availability tradeoff at the root of why decentralized
  freshness decisions are needed; pair with PACELC for the theory framing.

- **Viotti & Vukolić (2016)** — *Consistency in Non-Transactional Distributed Storage
  Systems.* ACM Computing Surveys 49(1), Article 19. DOI `10.1145/2926965`.
  Relevance: Q1 survey giving the formal lattice of 50+ consistency models — cite to
  place our "decision-time freshness" notion relative to established models.

- **Bermbach & Kuhlenkamp (2013)** — *Consistency in Distributed Storage Systems: An
  Overview of Models, Metrics and Measurement Approaches.* Proc. NETYS 2013, LNCS 7853,
  175–189. DOI `10.1007/978-3-642-40148-0_13`.
  Relevance: metrics/measurement of staleness — supports how we instrument and report
  freshness in the evaluation.

---

## Bucket 3 — Distributed consensus (POSITIONING only, not competing)

Used to argue our layer is orthogonal to / sits above replication and agreement
protocols. We do NOT claim to replace Raft/Paxos/BFT; Raft-LWW is a baseline substrate.

- **Ongaro & Ousterhout (2014)** — *In Search of an Understandable Consensus Algorithm
  (Raft).* Proc. USENIX ATC 2014, 305–319. (USENIX open access; ACM DL ID 2643666.)
  Relevance: Raft is the consensus substrate behind the Raft-LWW baseline; cite to
  separate "agreement on a log" from "deciding whether a cached read is actionable."

- **Lamport (1998)** — *The Part-Time Parliament (Paxos).* ACM Transactions on Computer
  Systems 16(2), 133–169. DOI `10.1145/279227.279229`. (See also Lamport, *Paxos Made
  Simple*, ACM SIGACT News 32(4), 2001, 51–58.)
  Relevance: seminal consensus reference for the positioning argument (agreement layer,
  not freshness-decision layer).

- **Castro & Liskov (1999/2002)** — *Practical Byzantine Fault Tolerance.* Proc. OSDI
  1999, 173–186; extended in ACM TOCS 20(4), 2002, 398–461.
  DOI `10.1145/571637.571640`.
  Relevance: BFT defines agreement under arbitrary faults; we cite to bound scope —
  our layer assumes the substrate handles agreement and addresses the decision above it.

- **Howard & Mortier (2020)** — *Paxos vs Raft: Have we reached consensus on distributed
  consensus?* Proc. PaPoC 2020 (EuroSys workshop), Article 8.
  DOI `10.1145/3380787.3393681`.
  Relevance: recent (2020) framing of the consensus landscape; supports the "consensus is
  a solved-and-orthogonal substrate" positioning.

- **Oki & Liskov (1988)** — *Viewstamped Replication.* Proc. PODC 1988, 8–17.
  DOI `10.1145/62546.62549` (verify).
  Relevance: primary-copy replication ancestor of modern consensus; optional historical
  anchor for the positioning paragraph.

- **Moraru, Andersen & Kaminsky (2013)** — *There Is More Consensus in Egalitarian
  Parliaments (EPaxos).* Proc. SOSP 2013, 358–372. DOI `10.1145/2517349.2517350`.
  Relevance: modern leaderless Paxos variant; cite if reviewers ask for current consensus
  state-of-the-art when arguing orthogonality.

---

## Bucket 4 — Business rules engines & DSLs

Drools, DMN, ANTLR/parser-based DSLs, policy-as-code. Our rules engine (JSON DSL +
ANTLR) is positioned against these; the novelty is the neutrosophic decision semantics,
not the rule-authoring substrate.

- **Object Management Group (2021)** — *Decision Model and Notation (DMN), v1.4.* OMG
  formal specification (formal/2022-08-01 for 1.4; verify exact version/date).
  Relevance: the standard for modeling operational decisions and decision tables — the
  most direct comparator for "declarative decision rules" without uncertainty semantics.

- **Proctor (2011)** — *Drools: A Rule Engine for Complex Event Processing.* Proc. AGTIVE
  2011, LNCS 7233, 2–2 (keynote). DOI `10.1007/978-3-642-34176-2_2` (verify).
  Relevance: canonical citation for the Rete-based production rule engine (Drools); the
  reference open-source rules engine we contrast against.

- **Forgy (1982)** — *Rete: A fast algorithm for the many pattern/many object pattern
  match problem.* Artificial Intelligence 19(1), 17–37.
  DOI `10.1016/0004-3702(82)90020-0`.
  Relevance: the matching algorithm underlying Drools-style engines; cite for engine
  background and to contrast deterministic boolean matching with neutrosophic scoring.

- **Parr (2013)** — *The Definitive ANTLR 4 Reference, 2nd ed.* Pragmatic Bookshelf.
  ISBN 9781934356999.
  Relevance: the parser generator we use to parse the JSON DSL; primary citation for the
  ANTLR-based grammar/rules front-end.

- **Parr (2009)** — *Language Implementation Patterns.* Pragmatic Bookshelf.
  ISBN 9781934356456.
  Relevance: DSL/interpreter design patterns supporting the rules-engine implementation
  description.

- **Mernik, Heering & Sloane (2005)** — *When and how to develop domain-specific
  languages.* ACM Computing Surveys 37(4), 316–344. DOI `10.1145/1118890.1118892`.
  Relevance: the canonical DSL methodology survey — justifies the design decision to
  introduce a JSON DSL rather than embed rules in general-purpose code.

- **Open Policy Agent / Rego — CNCF (project, 2016–present)** — *Open Policy Agent
  (OPA) and the Rego policy language.* (No single canonical paper; cite the CNCF project
  / docs, or an empirical study below.)
  Relevance: the modern "policy-as-code" comparator; OPA/Rego is declarative
  authorization without uncertainty/indeterminacy — sharpens our novelty.

- **Empirical study of Policy-as-Code adoption (2026)** — recent arXiv preprint on PaC
  adoption in OSS (arXiv 2601.05555, verify authors/title).
  Relevance: up-to-date evidence that policy-as-code is mainstream but boolean; supports
  framing neutrosophic decisioning as the missing capability.

---

## Bucket 5 — Neutrosophic sets & aggregation operators (CORE / NOVELTY)

Foundations (SVNS), the specific aggregation operators (SVNNWA/SVNNWG ≈ our
SVNNWAA/SVNNWGA), score/deneutrosophication functions, and — critically — the
**intersection with distributed systems / microservices / caching / consensus, which the
scan found to be essentially empty.**

### Foundations & operators

- **Smarandache (1998/1999)** — *A Unifying Field in Logics: Neutrosophy. Neutrosophic
  Probability, Set and Logic.* American Research Press.
  Relevance: origin of neutrosophy and the (T, I, F) triple — the theoretical root of the
  persistence-status encoding (persisted/indeterminate/absent ↔ T/I/F).

- **Wang, Smarandache, Zhang & Sunderraman (2010)** — *Single Valued Neutrosophic Sets.*
  Multispace and Multistructure 4, 410–413. (UNM digital repository.)
  Relevance: defines SVNS over [0,1]^3 — the exact mathematical object each data item
  carries; the primary definitional citation.

- **Ye (2014)** — *A multicriteria decision-making method using aggregation operators for
  simplified neutrosophic sets.* Journal of Intelligent & Fuzzy Systems 26(5),
  2459–2466. DOI `10.3233/IFS-130916` (verify).
  Relevance: introduces simplified-neutrosophic weighted arithmetic (SNWA) and weighted
  geometric (SNWG) averaging operators — the conceptual parents of our SVNNWAA/SVNNWGA.

- **Ye (2014)** — *Single-valued neutrosophic cross-entropy for multicriteria decision-
  making problems.* Applied Mathematical Modelling 38(3), 1170–1175.
  DOI `10.1016/j.apm.2013.07.020`.
  Relevance: SVNS scoring/cross-entropy for ranking — supports the deneutrosophy score
  function used to collapse a fused triple into an act/abstain decision.

- **Peng, Wang, Wang, Zhang & Chen (2016)** — *Simplified neutrosophic sets and their
  applications in multi-criteria group decision-making problems.* International Journal of
  Systems Science 47(10), 2342–2358. DOI `10.1080/00207721.2014.994050`.
  Relevance: rigorous treatment of SVNS aggregation operators and an improved comparison/
  score method — anchor for the operator choice and the fusion of peer views.

- **Liu & Wang (2014)** — *Multiple attribute decision-making method based on
  single-valued neutrosophic normalized weighted Bonferroni mean.* Neural Computing and
  Applications 25(7–8), 2001–2010. DOI `10.1007/s00521-014-1688-8` (verify).
  Relevance: alternative SVNN aggregation operator family; cite when justifying why
  weighted averaging/geometric (not Bonferroni) suits independent peer views.

- **Garg & Nancy (2018)** — *Some hybrid weighted aggregation operators under
  neutrosophic set environment and their applications to MCDM.* (verify exact title/
  venue/DOI; Garg has several closely titled SVNN operator papers 2016–2020.)
  Relevance: consolidated weighted-aggregation operator reference; useful supporting
  citation for operator properties (idempotency, monotonicity, boundedness).

### Neutrosophic applications adjacent to systems (to show the field, and the gap)

- **Abdel-Basset, Manogaran, Gamal & Smarandache (2019)** — *A group decision making
  framework based on neutrosophic TOPSIS approach for smart medical device selection.*
  Journal of Medical Systems 43, 38. DOI `10.1007/s10916-019-1156-1` (verify).
  Relevance: representative neutrosophic-MCDM-for-IoT/health application — shows the
  method is established for decision-making, but applied to selection, not runtime
  distributed state.

- **Nabeeh, Abdel-Basset, El-Ghareeb & Aboelfetouh (2019)** — *A novel intelligent
  framework for selection of IoT-related enterprises based on neutrosophic AHP/TOPSIS.*
  IEEE Access 7, 59559–59574. DOI `10.1109/ACCESS.2019.2908919` (verify).
  Relevance: same author cluster as the extended chapter; neutrosophic decision-making
  for IoT enterprises — adjacent, but still offline MCDM, not an in-band consistency
  layer.

- **Abdel-Basset, Nabeeh, El-Ghareeb & Aboelfetouh (2020)** — *Utilising neutrosophic
  theory to solve transition difficulties of IoT-based enterprises.* Enterprise
  Information Systems 14(9–10), 1304–1324. DOI `10.1080/17517575.2019.1633690` (verify).
  Relevance: most recent (2020) co-authored neutrosophic-systems work by this group;
  confirms the trajectory toward systems contexts but still at the planning/MCDM level —
  not implementation.

- **Neutrosophic security for fog / mobile-edge computing (2019)** — *A neutrosophic
  theory based security approach for fog and mobile-edge computing.* Computer Networks
  (Elsevier). DOI `10.1016/j.comnet.2018.11.027` (verify authors/exact title).
  Relevance: the closest neutrosophic-meets-distributed-infrastructure prior work — but
  it targets **security service selection**, not data freshness, caching, or state
  consistency. Reinforces that the state-consistency intersection is untouched.

- **Neutrosophic AHP for fog computing security management (2022)** — *A neutrosophic
  AHP-based computational technique for security management in a fog computing network.*
  The Journal of Supercomputing 78. DOI `10.1007/s11227-022-04674-2` (verify).
  Relevance: 2022 neutrosophic-in-fog work; again security/management decision support,
  not runtime distributed-state decisioning.

### Closest adjacent (non-neutrosophic) soft-computing-for-caching

- **Ali, Shamsuddin & Ismail (2011)** — *A survey of Web caching and prefetching.*
  International Journal of Advances in Soft Computing and its Applications 3(1), 18–44
  (verify); and **Calzarossa & Valli — fuzzy cache replacement** / **neuro-fuzzy
  client-side caching** (Expert Systems with Applications 39(2), 2012,
  DOI `10.1016/j.eswa.2011.06.011`, verify).
  Relevance: fuzzy logic HAS been applied to cache **replacement/prefetching**
  decisions — the nearest neighbor to our idea. But (a) it is fuzzy (single membership),
  not neutrosophic (no explicit indeterminacy/falsity), and (b) it optimizes hit ratio
  locally, not multi-peer freshness/consistency decisions. This is the sharpest contrast
  for the novelty claim.

> **Key finding for Bucket 5:** Repeated targeted searches
> ("neutrosophic + distributed systems / cache / consistency / consensus / staleness /
> microservices") returned **no** prior work applying single-valued neutrosophic sets to
> runtime distributed-state, cache-freshness, or consistency decisions. Neutrosophic
> theory in computing appears only as **offline MCDM** (vendor/device/enterprise
> selection) and **security service selection** for fog/edge. The decision-layer
> intersection this paper occupies is empty.

---

## Bucket 6 — Microservices benchmarking & reproducible evaluation

Standard benchmarks and the statistical-rigor literature underpinning our evaluation
methodology (≥30 reps, Holm correction, bootstrap CIs).

- **Gan et al. (Delimitrou group) (2019)** — *An Open-Source Benchmark Suite for
  Microservices and Their Hardware-Software Implications for Cloud & Edge Systems
  (DeathStarBench).* Proc. ASPLOS 2019, 3–18. DOI `10.1145/3297858.3304013`.
  Relevance: the de facto microservices benchmark suite, including a social network and
  e-commerce/media services — methodological precedent for our e-Commerce testbed.

- **Zhou, Peng, Xie, Sun, Ji, Li, Liu & Ding (2021)** — *Fault Analysis and Debugging of
  Microservice Systems: Industrial Survey, Benchmark System, and Empirical Study
  (TrainTicket).* IEEE Transactions on Software Engineering 47(2), 243–260.
  DOI `10.1109/TSE.2018.2887384`. (TSE Best Paper 2018.)
  Relevance: TrainTicket, a 41-service benchmark — the second standard testbed; supports
  the choice of a realistic multi-service e-Commerce evaluation.

- **Vitek & Kalibera (2011)** — *Repeatability, Reproducibility, and Rigor in Systems
  Research.* Proc. EMSOFT 2011, 33–38. DOI `10.1145/2038642.2038650`.
  Relevance: the manifesto on rigor in systems experiments — justifies our reps/seed/
  reproducibility protocol.

- **van der Kouwe, Andriesse, Bos, Giuffrida & Heiser (2018)** — *Benchmarking Crimes: An
  emerging threat in systems security.* arXiv 1801.02381 (and follow-on venue versions).
  Relevance: the 22 "benchmarking crimes" taxonomy — a checklist we explicitly avoid;
  cite in Threats to Validity.

- **Papadopoulos et al. (2021)** — *Methodological Principles for Reproducible Performance
  Evaluation in Cloud Computing.* IEEE Transactions on Software Engineering 47(8),
  1528–1543. DOI `10.1109/TSE.2019.2927908` (verify).
  Relevance: cloud-specific reproducible-evaluation principles — directly applicable to a
  containerized microservices testbed; supports the Methods/Threats sections.

- **Georges, Buytaert & Eeckhout (2007)** — *Statistically Rigorous Java Performance
  Evaluation.* Proc. OOPSLA 2007, 57–76. DOI `10.1145/1297027.1297033`.
  Relevance: seminal argument for confidence intervals and proper statistical treatment
  of performance data — backs our bootstrap-CI + multiple-repetition design.

- **Aghajani et al. (or comparable) microservices performance-testing survey** —
  (verify a recent 2022–2024 Q1 survey of microservices performance/observability
  evaluation). Relevance: situates our methodology within current evaluation practice.

---

## Novelty gap

The literature has, separately: (1) mature mechanisms for decentralized microservice
state and its impossibility limits (Saga/Event-Sourcing, the BAC theorem, VLDB data-
management studies); (2) a rich theory of consistency models, bounded/probabilistic
staleness, and convergent data types (CRDTs, COPS causal+, PBS, PACELC); (3) solved,
orthogonal agreement substrates (Raft, Paxos, PBFT); (4) declarative decision/rule
substrates (DMN, Drools/Rete, OPA/Rego, ANTLR-based DSLs) that are uniformly **boolean**;
and (5) a well-developed neutrosophic-set MCDM apparatus (SVNS, SVNNWA/SVNNWG operators,
score/deneutrosophication functions). What is **absent** is any work that brings (5) into
(1)–(4): no published method represents a data item's persistence/freshness status as a
single-valued neutrosophic (T, I, F) triple, lets peer microservices **fuse** their local
views with SVNN weighted-averaging/geometric operators, and **deneutrosophies** the
fused triple into a decentralized act/abstain decision about whether a cached value is
fresh and consistent enough to use. The closest neighbors fall short on exactly the
load-bearing axes: quorum/PBS reasoning is **boolean/probabilistic, not three-valued and
not indeterminacy-aware**; fuzzy-logic caching is **single-membership and local
hit-ratio-oriented, not neutrosophic and not multi-peer**; neutrosophic computing work is
**offline MCDM or security-service selection, never a runtime in-band consistency-decision
layer**; and consensus protocols solve **agreement, not freshness-of-decision** and thus
sit below, not in competition with, this layer. This paper fills that intersection — a
decentralized neutrosophic decision/consistency layer above the consistency substrate —
and is, to the best of this scan's reach, the first **implemented and empirically
evaluated** realization of the El-Ghareeb (2020) conceptual proposal.

---

## Candidate BibTeX keys

```
% Bucket 1 — microservices state & consistency
pardon2018bac
difrancesco2019architecting
soldani2018pains
laigner2021datamanagement
stefanko2019saga
richardson2018patterns
newman2021building

% Bucket 2 — CRDTs & consistency models
shapiro2011crdt
preguica2018crdt
lloyd2011cops
bailis2012pbs
abadi2012pacelc
brewer2012cap
viotti2016consistency
bermbach2013consistency

% Bucket 3 — consensus (positioning)
ongaro2014raft
lamport1998paxos
castro1999pbft
howard2020consensus
moraru2013epaxos

% Bucket 4 — rules engines & DSLs
omg2021dmn
proctor2011drools
forgy1982rete
parr2013antlr
parr2009lip
mernik2005dsl
opa2016rego

% Bucket 5 — neutrosophic sets & operators (core/novelty)
smarandache1998neutrosophy
wang2010svns
ye2014operators
ye2014crossentropy
peng2016simplified
liu2014bonferroni
garg2018hybrid
abdelbasset2019topsis
nabeeh2019iot
abdelbasset2020transition
neutro2019fogsecurity
neutro2022fogahp
fuzzy2012neurofuzzycache

% extended conceptual basis
elghareeb2020chapter

% Bucket 6 — benchmarking & rigor
gan2019deathstarbench
zhou2021trainticket
vitek2011rigor
vanderkouwe2018crimes
papadopoulos2021reproducible
georges2007statistically
```

> **Reference-audit reminder:** before manuscript use, run the
> `REFERENCE_AUDIT_ORDERS.md` sweep — resolve every "(verify)" tag, confirm each DOI
> against the publisher landing page, and add a DOI to every journal entry. Do not let
> any "(verify)" item reach the bibliography unconfirmed (Inadmissibility rule R1 applies
> to citations as well).
