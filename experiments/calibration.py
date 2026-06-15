"""Load and content-hash the locked calibration (Rule R6).

The SHA-256 is computed over the canonical (sorted-key, compact) JSON encoding so it is stable
regardless of formatting. Every results CSV header carries this hash; the aggregator refuses to
mix CSVs whose hashes differ.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "calibration.json"


@lru_cache(maxsize=1)
def load_calibration(path: str | None = None) -> dict[str, Any]:
    p = Path(path) if path else CONFIG_PATH
    return json.loads(p.read_text(encoding="utf-8"))


def calibration_sha256(calibration: dict[str, Any] | None = None) -> str:
    cfg = calibration if calibration is not None else load_calibration()
    canonical = json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def derive_seed(master_seed: int, *parts: Any) -> int:
    """Per-cell deterministic seed (Rule R5): uint64 of SHA-256(master | canonical tuple).

    NOTE: callers must EXCLUDE the system name from ``parts`` for the environment RNG, so every
    strategy is evaluated on an identical decision stream within a (cell-minus-system, trial).
    """
    tuple_str = "|".join(str(p) for p in (master_seed, *parts))
    digest = hashlib.sha256(tuple_str.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")
