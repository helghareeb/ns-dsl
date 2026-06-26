# ns-dsl
> A decentralized neutrosophic decision layer that lets microservices act-or-abstain on global-state freshness, trading consistency for availability rather than claiming superiority over consensus.

Microservices decide over global state they do not own, and the only cross-service signal is a cache that may hold uncommitted values a boolean fresh/stale flag cannot express. This repository implements a decentralized layer in which each item carries a single-valued neutrosophic triple `(T, I, F)` for persistence status; peers fuse their views with weighted operators and a deneutrosophy score and act or abstain without central authority. Against consistency baselines the layer occupies a Pareto interior (e.g. at a 10% failure rate it cuts the stale-decision rate by 16.7 points versus last-writer-wins and stays 88% available under partition where a primary drops to 45%); honestly, it does **not** beat a calibrated single-probability gate on the headline trade-off, the value-selection path is **not** Byzantine-robust, and it makes no superiority claim over consensus — the contribution is a transparent, reproducible trade-off.

## Key contributions
- A decentralized `(T, I, F)`-aggregating decision protocol for global-state freshness: peers encode storage status as single-valued neutrosophic numbers, fuse views with weighted neutrosophic operators and a deneutrosophy score, and act or abstain with no central authority — a per-item freshness decision above the consistency substrate, not a replication or consensus protocol.
- Formal guarantees: one-round termination and partition tolerance, conservative-safety and optimistic-liveness bounds bracketing the act/abstain gate (generalized to a graded encoding), and Byzantine gate-resistance under robust aggregation — with an explicit proposition that gate-robustness does **not** imply value-robustness.
- A two-axis audit that the result is not a design artefact: an aggregation-operator panel (Einstein, Hamacher, Dombi, Aczél–Alsina, Bonferroni) over a graded encoding, a deneutrosophy-score panel, and an equal-budget metaheuristic tuning of the threshold and peer weights (seven optimizers; tuning gain real but modest and regime-specific, consistent with No-Free-Lunch).
- A robustness study under an adversarial (Byzantine) value-fabrication model with median-, trimmed-mean-, and Krum-based aggregation, reported as it stands: robust aggregators degrade together with the averaging operators because the exposure is value selection, which coordinate-wise robustness does not govern.
- A reproducible evaluation on an e-commerce testbed against consistency baselines (strong, eventual, quorum, partial-quorum) plus a calibrated single-probability gate, with a cross-domain feature-store check; ≥50 repetitions per cell across five seeds, Holm-corrected comparisons, and bootstrap confidence intervals, with every number regenerable from committed code, a content-hashed calibration, and recorded seeds.

## Repository structure
| Path | Purpose |
|------|---------|
| `src/nsdsl/` | Core library: `neutro/` operators, `dsl/` ANTLR parser, `rules/`, `consensus/`, `bus/`, `oracle/`, `baselines/`, `optim/` |
| `services/` | FastAPI e-commerce microservices (products / orders / users / frontend) |
| `docker/` | Docker Compose testbed (Redis event bus, Postgres, Toxiproxy fault/latency injection) |
| `grammar/` | ANTLR JSON grammar and pinned ANTLR 4.13.2 jar |
| `experiments/` | Harness, calibration, sweeps, and the single canonical aggregator (`analyze_results.py`) |
| `bench/` | Measured-latency benchmark on the real HTTP testbed |
| `config/` | `calibration.json` (content-hashed) and scenario configs |
| `datasets/` | Seeded synthetic-data generator for the headline evaluation |
| `data/` | Optional external real-trace loaders (gitignored downloads; not used for the submitted headline numbers) |
| `results/` | `raw/` per-trial CSVs (gitignored), `tables/` committed summaries, `figures/` |
| `paper/` | Manuscript (`wlscirep`), tables, and continuity docs |
| `tests/` | pytest suite mirroring `src/` |

## Reproducing
```bash
# Setup
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'

# (optional, only if the grammar changed) regenerate the ANTLR parser — needs Java
make antlr-gen

# 1. tests must be green
PYTHONPATH=src:. .venv/bin/python -m pytest -q tests/

# 2. fit the acceptance threshold tau on held-out calibration seeds, then freeze
PYTHONPATH=src:. .venv/bin/python -m experiments.calibrate

# 3. run the full validated grid (hash-stamped raw CSVs)
PYTHONPATH=src:. .venv/bin/python -m experiments.run_all

# 4. the single canonical aggregator: summary + Holm pairwise + multi-seed validation
PYTHONPATH=src:. .venv/bin/python -m experiments.analyze_results

# 5. sensitivity sweep and measured latency on the real HTTP testbed
PYTHONPATH=src:. .venv/bin/python -m experiments.run_tier_b
PYTHONPATH=src:. .venv/bin/python -m bench.latency_bench

# 6. figures and LaTeX tables (read only the aggregator / measurement outputs)
PYTHONPATH=src:. .venv/bin/python -m experiments.make_figures
PYTHONPATH=src:. .venv/bin/python -m experiments.make_tables

# 7. build the manuscript
cd paper && latexmk -pdf manuscript.tex
```
Common targets are wrapped in the `Makefile` (`make dev`, `make test`, `make experiments`, `make figures`, `make tables`, `make paper`; `make up`/`make down` for the Docker testbed). The full grid runs in a few minutes on a laptop (pure-Python discrete-event simulation). See [REPRODUCE.md](REPRODUCE.md) for the end-to-end path and how to trace any paper number to its source cell.

## Reproducibility
Every figure and table regenerates end-to-end from committed code, the content-hashed `config/calibration.json` (its SHA-256 is stamped into each results CSV header), and the recorded random seeds. A single canonical aggregator (`experiments/analyze_results.py`) produces every statistic from `results/raw/*.csv`, and aborts if input CSVs disagree on the calibration hash. Raw per-trial outputs are gitignored; the generators and the aggregated result summaries are committed, so no bulk data is needed to reproduce the numbers.

## Data availability
The headline evaluation uses **no third-party datasets**: all data are generated by the evaluation simulator under the fixed, content-hashed calibration and recorded seeds described in the Methods. The aggregated result summaries underlying every figure and table are provided with the article as **Supplementary Information**; together with the figure and table generators they regenerate every reported number. The complete raw per-trial outputs are archived in Zenodo (DOI: 10.5281/zenodo.XXXXXXX) and the implementation is archived in Zenodo (DOI: 10.5281/zenodo.YYYYYYY). During peer review both records are under **restricted access**; editors and reviewers are granted immediate access through a private repository link provided to the editorial office, and they are released openly (CC BY 4.0 for data, MIT for code) **upon publication**. The optional real-trace loaders under `data/` (Online Retail II, UCI, CC BY 4.0; Intel Lab Data, MIT CSAIL, open research; IEEE-CIS / ULB / PaySim fraud, Kaggle; Twitter cache trace, OSDI'20, CC BY 4.0) ship `download.sh` scripts for an out-of-scope real-trace check and are not part of the submitted headline numbers.

## Paper
**A decentralized neutrosophic decision layer for global-state freshness in microservices architectures** — H. A. El-Ghareeb. Target venue **Scientific Reports**; status **submitted (2026)**, under review.

## License
Released under the MIT License — see [LICENSE](LICENSE).
