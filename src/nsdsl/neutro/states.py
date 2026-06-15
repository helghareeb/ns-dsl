"""Canonical neutrosophic persistence states for a data item.

Maps a data item's storage status to a single-valued neutrosophic number, per the 2020
chapter (section 2.8.2):

    persisted in DB        -> (1, 0, 0)   truth      = committed
    in cache only          -> (0, 1, 0)   indeterminacy = unconfirmed
    neither (default)      -> (0, 0, 1)   falsity    = never seen

ERRATUM: the chapter prints the default state as (0, 1, 0), duplicating CACHED. The intended
value is (0, 0, 1): a value that was never seen/persisted must read as *falsity*, not
*indeterminacy*. This matters for consensus -- a missing or late peer contributes DEFAULT, and
treating "absent" as "cached/unconfirmed" would inflate the indeterminacy axis and bias the
aggregate. We implement the corrected (0, 0, 1) and document the fix in the manuscript.
"""
from __future__ import annotations

from .svnn import SVNN

PERSISTED = SVNN(1.0, 0.0, 0.0)
CACHED = SVNN(0.0, 1.0, 0.0)
DEFAULT = SVNN(0.0, 0.0, 1.0)

# String tags as they appear in the JSON DSL (Listing 2.2 uses "(1,0,0)" etc.).
_BY_TUPLE = {
    (1.0, 0.0, 0.0): PERSISTED,
    (0.0, 1.0, 0.0): CACHED,
    (0.0, 0.0, 1.0): DEFAULT,
}


def parse_status(text: str) -> SVNN:
    """Parse a status string like "(1,0,0)" (Listing 2.2) into an SVNN.

    Recognizes the three canonical states by value but also accepts any in-range triple.
    """
    cleaned = text.strip().lstrip("(").rstrip(")")
    parts = [p.strip() for p in cleaned.split(",")]
    if len(parts) != 3:
        raise ValueError(f"expected a 3-tuple status string, got {text!r}")
    t, i, f = (float(p) for p in parts)
    return _BY_TUPLE.get((t, i, f), SVNN(t, i, f))
