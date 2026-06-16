# RESUME — ns-dsl

**Coordinated by** `~/Documents/github/ns-SCADA/recover_all.sh` (sequence position 2). See
`ns-SCADA/STATUS.md` for the live cross-repo state.

- **State:** re-running fresh after the crash (the Tier-A eval is NOT cell-resumable, so partial
  `results/raw/*` is wiped and the run restarted).
- **Venv:** `.venv` (Python 3.13). **Data:** present (`data/`, 88 MB; raw gitignored, re-fetch via
  `data/online_retail_ii/download.sh`).
- **Standalone resume:** `rm -rf results/raw/* && .venv/bin/python -m experiments.calibrate && \
  .venv/bin/python -m experiments.run_all && .venv/bin/python -m experiments.analyze_results`
  (or `make experiments`). Run detached: wrap with `setsid nohup … &`.
- Estimated runtime: ~hours (decision simulation, CPU).
