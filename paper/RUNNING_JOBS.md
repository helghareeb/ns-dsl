# RUNNING_JOBS — long-running experiment ledger (N2)

Every long background run that produces manuscript-grade numbers is logged here: command, log
path, expected artifacts, status, started/completed. Single source of truth for in-flight
experiments.

| Job | Command | Artifacts | Status | Notes |
|-----|---------|-----------|--------|-------|
| **ENRICHED grid (G9)** | `calibrate -> run_all -> analyze_results` | `tau_fit.csv` (15 systems), `raw_seed*.csv` (22 strategies), `per_config_summary.csv` | 🟡 **running (2026-06-21 ~20:12)** | enriched: Axis-A operator panel + graded encoding, Axis-A' score panel, Byzantine-robust aggregators, freshness-SLO baseline. 5 seeds × 3 scenarios × 4 φ × 2 partition × 50 reps × 300 decisions × 22 systems. Same R6 hash (no calibration.json change) -> extends the validated baseline; waa/wga reproduce byte-for-byte. Log `/tmp/nsdsl_enriched_grid.log`. Est. ~2 h. |
| tau calibration (submitted) | `python -m experiments.calibrate` | `results/tables/tau_fit.csv` | ✅ superseded by the enriched fit | held-out seeds 770001-3; S2-waa τ=0.70, S1/S3-waa τ=0.30, wga τ=0.30 |
| Full Tier-A eval | `python -m experiments.run_all` | `results/raw/raw_seed{20260615,16,17}.csv` | 🟡 running | 3 seeds × 3 scenarios × 3 φ × 2 partition × 30 reps × 200 decisions × 8 systems; status=validated (fitted τ) |
| Aggregate | `python -m experiments.analyze_results` | `per_config_summary.csv`, `pairwise_tests.csv`, `multiseed_validation.csv` | ⬜ after run | Holm + 5000× bootstrap + multi-seed sign agreement |

Tier-B sensitivity sweeps and the Docker real-latency runs are pending (M10b cont. / M5).

## Scaled Q1 run (2026-06-16)

| Job | Command | Artifacts | Status |
|-----|---------|-----------|--------|
| Scaled chain | calibrate -> run_all -> analyze -> tier_b -> s3 -> latency -> throughput | summary/pairwise/multiseed/sensitivity/s3/latency/throughput CSVs | 🟡 running |

Scaled design: 5 seeds, 50 reps/cell, 300 decisions/trial, phi in {0,0.1,0.2,0.3}, 9 systems
(adds PBS bounded-staleness baseline). Adds measured throughput (decisions/sec under load) and a
real Docker container run of the peer testbed.
