# External datasets (real-trace evaluation, WS1)

Raw downloads are **gitignored**; each dataset ships a `download.sh` + the loader that turns it into
a `TraceProfile`, so every number stays regenerable without committing bulk data (Rules R1/G5/N15).
Every results CSV embeds the trace content-hash alongside the calibration SHA-256 (R6).

| Dataset | Drives | License | Get it |
|---------|--------|---------|--------|
| **Online Retail II** (UCI 502) | S1 pricing: real key-skew (StockCode Zipf), abort/dirty rate (cancellation invoices), arrival burstiness incl. seasonal peak | CC BY 4.0 | `bash data/online_retail_ii/download.sh` then `python -m experiments.traces.prep_retail` |
| **Intel Lab Data** (MIT CSAIL) | IoT domain (WS2): sensor write stream, dropout → indeterminacy, staleness windows | open (research) | `bash data/intel_lab/download.sh` |
| IEEE-CIS / ULB / PaySim (fraud, S2) | real fraud labels → precision/recall/F1 | Kaggle (DbCL / comp. rules) | needs a Kaggle API key (`~/.kaggle/kaggle.json`); see `data/fraud/download.sh` |
| Twitter cache-trace (OSDI'20) | dirty-read/key-skew calibration | CC BY 4.0 | large (S3); see `data/cache/download.sh` for a cluster sample |

The loaders measure parameters (e.g., the empirical dirty/abort rate that replaces the hand-set
`dirty_cache_prob` in `config/calibration.json`); the synthetic model is retained as a labeled
controlled ablation.
