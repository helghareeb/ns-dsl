#!/usr/bin/env bash
# UCI Online Retail II (dataset 502, CC BY 4.0). Raw is gitignored; this script + the loader
# are committed so the evaluation is regenerable (R1/N15).
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)/raw"
mkdir -p "$DIR"
curl -fsSL -o "$DIR/online_retail_II.zip" \
  https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip
( cd "$DIR" && unzip -o online_retail_II.zip )
echo "downloaded -> $DIR ; now run: PYTHONPATH=src:. python -m experiments.traces.prep_retail"
