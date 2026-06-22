"""Graded peer-confidence encoding (enriches the crisp persisted/cached/absent corners).

The submitted model encodes each peer's view as a crisp SVNN corner: PERSISTED=(1,0,0),
CACHED=(0,1,0), absent=(0,0,1). On those corners the t-conorm aggregation operators collapse to a
single OR-behaviour (only the geometric WGA differs), so the operator panel cannot be audited. This
module maps a peer's *kind* plus an OBSERVABLE recency signal -- its version lag relative to the most
up-to-date reachable peer (no oracle) -- to a graded SVNN, so the panel differentiates and the
neutrosophic machinery exercises its graded nature.

Semantics: T = confidence the held value is the committed-current truth; I = unconfirmedness
(cache / can't tell); F = confidence the value is stale/superseded/absent. Confidence decays with
the relative lag (`lag_scale` knob); a lone anomalously-high version is treated as a suspected dirty
(uncommitted future) write and shifts mass to falsity. The crisp encoding remains the conservative
baseline; this graded encoding is an audited enrichment. The numeric anchors below are a documented,
tunable design choice (overridable via calibration.json -> "grade_encoding").
"""

from __future__ import annotations

from collections.abc import Sequence

from .states import CACHED, DEFAULT, PERSISTED
from .svnn import SVNN

# Default graded anchors (tunable). Each peer kind maps (freshness in [0,1]) -> (T, I, F).
GRADE_DEFAULTS: dict[str, float] = {
    "lag_scale": 2.0,        # larger => confidence decays more slowly with version lag
    "persist_T_base": 0.50,  # persisted: T = base + (1-base)*fresh  (=> 1 when fresh)
    "persist_I": 0.10,
    "persist_F_stale": 0.40,  # stale persisted gains falsity (it WAS committed, now superseded)
    "cache_T": 0.45,         # fresh clean cache: holds the truth but unconfirmed
    "cache_I_base": 0.55,
    "cache_I_stale": 0.10,
    "cache_F_base": 0.10,
    "cache_F_stale": 0.25,
    "dirty_T": 0.15,         # suspected dirty (uncommitted future) write
    "dirty_I": 0.45,
    "dirty_F": 0.45,
    "absent_T": 0.05,
    "absent_I": 0.10,
    "absent_F": 0.85,
}


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def _kind(status: SVNN) -> str:
    """Recover the peer kind from its crisp status SVNN."""
    if status is PERSISTED or status == PERSISTED:
        return "persisted"
    if status is CACHED or status == CACHED:
        return "cached"
    return "absent"


def grade(status: SVNN, rel_lag: int, *, suspect_dirty: bool = False,
          params: dict[str, float] | None = None) -> SVNN:
    """Map a peer's crisp ``status`` + observed relative version lag to a graded SVNN.

    rel_lag : (max reachable peer version) - (this peer's version), clamped at 0.
    suspect_dirty : this peer alone holds an anomalously high version (likely an uncommitted write).
    """
    p = params or GRADE_DEFAULTS
    fresh = 1.0 / (1.0 + max(0, rel_lag) / p["lag_scale"])
    kind = _kind(status)
    if suspect_dirty and kind == "cached":
        return SVNN(_clamp01(p["dirty_T"] * fresh), _clamp01(p["dirty_I"]), _clamp01(p["dirty_F"]))
    if kind == "persisted":
        return SVNN(
            _clamp01(p["persist_T_base"] + (1.0 - p["persist_T_base"]) * fresh),
            _clamp01(p["persist_I"]),
            _clamp01(p["persist_F_stale"] * (1.0 - fresh)),
        )
    if kind == "cached":
        return SVNN(
            _clamp01(p["cache_T"] * fresh),
            _clamp01(p["cache_I_base"] + p["cache_I_stale"] * (1.0 - fresh)),
            _clamp01(p["cache_F_base"] + p["cache_F_stale"] * (1.0 - fresh)),
        )
    return SVNN(_clamp01(p["absent_T"]), _clamp01(p["absent_I"]), _clamp01(p["absent_F"]))


def grade_views(
    statuses: Sequence[SVNN],
    versions: Sequence[int],
    *,
    params: dict[str, float] | None = None,
) -> list[SVNN]:
    """Grade a set of peer views using their observable versions only (decentralized).

    The freshness reference is the maximum version among the peers; a peer whose version strictly
    exceeds every other (a lone maximum above the runner-up) is flagged as a suspected dirty write.
    """
    if not statuses:
        return []
    present = [v for v in versions]
    max_v = max(present)
    runner_up = sorted(present)[-2] if len(present) >= 2 else max_v
    out: list[SVNN] = []
    for status, v in zip(statuses, versions):
        if status is DEFAULT or status == DEFAULT:
            out.append(grade(DEFAULT, 0, params=params))
            continue
        rel_lag = max_v - v
        suspect = v > runner_up and v > 0
        out.append(grade(status, rel_lag, suspect_dirty=suspect, params=params))
    return out
