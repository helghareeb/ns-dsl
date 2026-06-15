# RUNNING_JOBS — long-running experiment ledger (N2)

Every long background run that produces manuscript-grade numbers is logged here: command, log
path, expected artifacts, status, started/completed. Single source of truth for in-flight
experiments.

| Job | Command | Artifacts | Status | Notes |
|-----|---------|-----------|--------|-------|
| tau calibration | `python -m experiments.calibrate` | `results/tables/tau_fit.csv` | ✅ done | held-out seeds 770001-2; S2-waa τ=0.70 (conservative), S1/S3-waa τ=0.30, wga τ=0.30 |
| Full Tier-A eval | `python -m experiments.run_all` | `results/raw/raw_seed{20260615,16,17}.csv` | 🟡 running | 3 seeds × 3 scenarios × 3 φ × 2 partition × 30 reps × 200 decisions × 8 systems; status=validated (fitted τ) |
| Aggregate | `python -m experiments.analyze_results` | `per_config_summary.csv`, `pairwise_tests.csv`, `multiseed_validation.csv` | ⬜ after run | Holm + 5000× bootstrap + multi-seed sign agreement |

Tier-B sensitivity sweeps and the Docker real-latency runs are pending (M10b cont. / M5).
