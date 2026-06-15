# Reproducing every number in the paper

Rule R1: every figure and table is regenerable end-to-end from committed code +
`config/calibration.json` (content-hashed, SHA-256 stamped into each results CSV) + a recorded
seed. One canonical aggregator (`experiments/analyze_results.py`) produces every statistic.

## Setup
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

## One path from scratch to the manuscript PDF
```bash
# 0. (only if grammar changed) regenerate the ANTLR parser — needs Java
make antlr-gen

# 1. tests must be green
PYTHONPATH=src:. .venv/bin/python -m pytest -q tests/          # 70 passing

# 2. fit the acceptance threshold tau on HELD-OUT calibration seeds, then freeze
PYTHONPATH=src:. .venv/bin/python -m experiments.calibrate     # -> results/tables/tau_fit.csv

# 3. run the full validated grid (3 seeds, >=30 reps/cell) -> hash-stamped raw CSVs
PYTHONPATH=src:. .venv/bin/python -m experiments.run_all       # -> results/raw/raw_seed*.csv

# 4. THE single canonical aggregator: summary + Holm pairwise + multi-seed validation
PYTHONPATH=src:. .venv/bin/python -m experiments.analyze_results
#   -> results/tables/{per_config_summary,pairwise_tests,multiseed_validation}.csv

# 5. sensitivity sweep (vary R, rho) and measured latency on the real HTTP testbed
PYTHONPATH=src:. .venv/bin/python -m experiments.run_tier_b    # -> results/tables/sensitivity.csv
PYTHONPATH=src:. .venv/bin/python -m bench.latency_bench       # -> results/tables/latency_measured.csv

# 6. figures + LaTeX tables (read ONLY the aggregator / measurement outputs)
PYTHONPATH=src:. .venv/bin/python -m experiments.make_figures  # -> results/figures/*.pdf
PYTHONPATH=src:. .venv/bin/python -m experiments.make_tables   # -> paper/tables/*.tex

# 7. build the manuscript
cd paper && latexmk -pdf manuscript.tex                        # -> paper/manuscript.pdf

# Docker deployment of the same peer topology (optional, for fidelity):
#   docker compose -f docker/docker-compose.yml up --build
```

A `--quick` flag on `run_all` does a 1-seed smoke run for development; full runs (no flag) are
tagged `status=validated` in every CSV header.

## Tracing a paper number to its source
Pick any value in `paper/tables/headline_s2.tex` or a figure → it is a cell in
`results/tables/per_config_summary.csv`, keyed by `(scenario, system, failure_inject_phi,
partition)`, computed from `results/raw/raw_seed*.csv` whose header carries the
`calibration_sha256`. The aggregator aborts if input CSVs disagree on that hash (Rule R6).

## Hardware / runtime
The full grid runs in a few minutes on a laptop (pure-Python discrete-event simulation). Latency
reported in the paper is an analytical network model; measured wall-clock latency on a Dockerized
testbed is ongoing work (see `paper/Q1_HANDOFF.md`).
