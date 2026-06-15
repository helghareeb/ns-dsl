"""Weighted aggregation operators for single-valued neutrosophic numbers.

SVNNWAA -- weighted arithmetic averaging (chapter Eq. 2.6):
    T = 1 - prod_j (1 - T_j)^w_j ,  I = prod_j (I_j)^w_j ,      F = prod_j (F_j)^w_j

SVNNWGA -- weighted geometric averaging (chapter Eq. 2.7):
    T = prod_j (T_j)^w_j ,          I = 1 - prod_j (1 - I_j)^w_j, F = 1 - prod_j (1 - F_j)^w_j

Weights w_j are non-negative and normalized to sum to 1. Products are evaluated in log-space to
avoid floating-point underflow when many peers participate (large n in the S3 clone scenario),
with explicit zero handling: prod_j v_j^w_j == 0 exactly if any v_j == 0 (with w_j > 0). For
SVNNWGA this means a single peer reporting T_j = 0 collapses the aggregate truth to 0 -- the
correct, conservative semantics (one peer certain the value is not committed vetoes "fresh").
"""
from __future__ import annotations

import math
from collections.abc import Sequence

from .svnn import SVNN

_TOL = 1e-12


def normalize_weights(weights: Sequence[float] | None, n: int) -> list[float]:
    """Return non-negative weights summing to 1. ``None`` yields uniform weights."""
    if weights is None:
        return [1.0 / n] * n
    if len(weights) != n:
        raise ValueError(f"expected {n} weights, got {len(weights)}")
    if any(w < 0 for w in weights):
        raise ValueError(f"weights must be non-negative, got {list(weights)}")
    total = math.fsum(weights)
    if total <= _TOL:
        raise ValueError("weights sum to (near) zero; cannot normalize")
    return [w / total for w in weights]


def _wprod(values: Sequence[float], weights: Sequence[float]) -> float:
    """prod_j values_j ** weights_j, in log-space. Returns 0.0 if any value_j == 0 (w_j > 0)."""
    acc = 0.0
    for v, w in zip(values, weights):
        if w == 0.0:
            continue
        if v <= 0.0:
            return 0.0
        acc += w * math.log(v)
    return math.exp(acc)


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def svnnwaa(zs: Sequence[SVNN], weights: Sequence[float] | None = None) -> SVNN:
    """SVNN weighted arithmetic averaging operator (Eq. 2.6)."""
    if not zs:
        raise ValueError("svnnwaa requires at least one SVNN")
    w = normalize_weights(weights, len(zs))
    t = 1.0 - _wprod([1.0 - z.T for z in zs], w)
    i = _wprod([z.I for z in zs], w)
    f = _wprod([z.F for z in zs], w)
    return SVNN(_clamp01(t), _clamp01(i), _clamp01(f))


def svnnwga(zs: Sequence[SVNN], weights: Sequence[float] | None = None) -> SVNN:
    """SVNN weighted geometric averaging operator (Eq. 2.7)."""
    if not zs:
        raise ValueError("svnnwga requires at least one SVNN")
    w = normalize_weights(weights, len(zs))
    t = _wprod([z.T for z in zs], w)
    i = 1.0 - _wprod([1.0 - z.I for z in zs], w)
    f = 1.0 - _wprod([1.0 - z.F for z in zs], w)
    return SVNN(_clamp01(t), _clamp01(i), _clamp01(f))
