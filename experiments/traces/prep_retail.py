"""One-time prep: UCI Online Retail II xlsx -> compact cached CSV the loader reads.

Downloads are gitignored; this prep + the loader are committed so results stay regenerable
(R1/N15). Source: UCI ML Repository dataset 502 (Online Retail II), CC BY 4.0.
Run:  PYTHONPATH=src:. python -m experiments.traces.prep_retail
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "online_retail_ii" / "raw" / "online_retail_II.xlsx"
OUT = ROOT / "data" / "online_retail_ii" / "online_retail_ii.csv"
COLS = ["Invoice", "StockCode", "Quantity", "Price", "InvoiceDate", "Customer ID"]


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"missing {RAW}; run data/online_retail_ii/download.sh first")
    frames = []
    for sheet in ("Year 2009-2010", "Year 2010-2011"):
        df = pd.read_excel(RAW, sheet_name=sheet, usecols=COLS, engine="openpyxl")
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out["Invoice"] = out["Invoice"].astype(str)
    out["StockCode"] = out["StockCode"].astype(str)
    out.to_csv(OUT, index=False)
    cancels = out["Invoice"].str.startswith("C").mean()
    print(f"wrote {OUT}: {len(out):,} rows; cancellation(abort) fraction = {cancels:.4f}")


if __name__ == "__main__":
    main()
