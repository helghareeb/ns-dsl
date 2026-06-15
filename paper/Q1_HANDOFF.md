# Q1_HANDOFF — restart-continuity ledger

> Single source of truth for picking up this build mid-flight. Updated at each milestone.
> Target venue: **Future Generation Computer Systems** (Elsevier, Q1). Plan:
> `~/.claude/plans/inside-docs-you-will-parsed-bentley.md`.

## What this project is
A fresh, reproducible artifact + extended journal paper backing the conceptual 2020 Elsevier
book chapter (`docs/ns-dsl.pdf`). Contribution = a DSL/rules engine **and** a decentralized
neutrosophic `(T,I,F)`-aggregating **decision layer** for global-state decisions in microservices,
evaluated against baselines on 3 e-Commerce scenarios with a ground-truth oracle.

**Honest-claim guardrail:** the neutrosophic layer is a per-item freshness/consistency *decision*
layer, NOT a Raft/Paxos replacement. Apples-to-apples control = quorum-of-booleans. See
`PROJECT_BUILD_RULES.md`.

## Status (done / in-flight / next)

| Milestone | State | Notes |
|-----------|-------|-------|
| M0 repo skeleton | ✅ done | git, pyproject, Makefile, layout, rules mirror |
| M1 neutrosophic core | ✅ done | SVNN, SVNNWAA/SVNNWGA (log-space), score, (0,0,1) erratum fix |
| M2 DSL/parser | ✅ done | ANTLR JSON parser committed; Listings 2.1/2.2 parse |
| M3 rules engine | ✅ done | Business Rule 001 fires; tag sets; provenance |
| M4 S1 pricing (single-node) | ✅ done | personalized price over in-proc bus |
| M6 consensus + oracle | ✅ done | aggregate/protocol + god_log/truth; WAA/WGA, partition+heal, convergence |
| M8 baselines | ✅ done | 6 baselines + ours under one read-decision interface |
| M9 harness + aggregator | ✅ done | run_all.py + analyze_results.py (Holm + bootstrap) + figures |
| M7 S3 clone catch-up | ✅ done | log replay -> consensus-consistent state |
| M10 calibrate + full runs | ✅ done | tau fit (held-out) + 3-seed validated grid + multi-seed (96%) |
| M11 manuscript | ✅ draft | elsarticle, N5 order, compiles to 16pp; numbers from aggregator |
| M10c Tier-B sensitivity | ✅ done | sweep R, rho -> sensitivity.csv + figure f6 |
| M5 measured latency | ✅ done | real localhost HTTP testbed (bench/) + Docker Compose deploy files; figure f5 |
| Reference audit | ✅ applied | fixed georges DOI, pardon author, re-added 2 Springer DOIs (underscore pkg) |
| GitHub remote | ✅ pushed | git@github.com:helghareeb/ns-dsl.git (main) |

**Test suite:** 70 passing (`make test`). **Validated results exist** (3 seeds, Holm, bootstrap;
`status=validated`). **Manuscript compiles** (`paper/manuscript.pdf`, 13 pp).
**End-to-end reproducible** via `REPRODUCE.md`.

### Headline validated numbers (S2, phi=0.1)
- neutro-waa stale 0.245 vs lww 0.416 (-41%), naive 0.506 (-52%); Holm p<1e-6, d=-6.05 vs lww.
- availability under transient partition: neutro-waa 0.88 vs centralized/raft 0.46 (d=21.6).
- vs boolean quorum: comparable stale at ~2.3x availability (0.94 vs 0.40).

## Reordering note
M6 (consensus + oracle) does not require Docker — the bus is a `Protocol`, so N peers can be
simulated in-process. Building M6 in-process next is higher-value than M5; Docker becomes a
deployment/fidelity wrapper around the same logic.

## Where things live
- Core lib: `src/nsdsl/{neutro,dsl,rules,bus}`, `src/nsdsl/state_store.py`
- Services: `services/{users,products}/logic.py` (transport-agnostic; M5 wraps in FastAPI)
- Tests: `tests/` mirror the modules
- Grammar + ANTLR jar: `grammar/` (regenerate with `make antlr-gen`)

## Open items / decisions pending
- Lock exact El-Ghareeb 2019 (NSS 25:136) operator forms via a literature check before any cell
  is marked `validated` (we currently use standard SVNN forms — see `neutro/operators.py`).
- `config/calibration.json` not yet created (needed at M9 for R6 hashing).
- Git remote not set; local commits only (push when a remote exists).
