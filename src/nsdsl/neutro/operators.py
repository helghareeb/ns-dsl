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


# === Operator panel (Axis A of the enriched audit) ===========================
# Parameterised SVNN weighted-averaging operators from recent (2018-2024) MCDM work, added so
# the aggregation rule -- not just the optimistic/conservative WAA/WGA pair -- can be audited.
# IMPORTANT: with the crisp persisted/cached/absent corners ((1,0,0)/(0,1,0)/(0,0,1)) the
# t-conorm operators (Einstein, Hamacher, Dombi, Aczel-Alsina arithmetic) all collapse to WAA's
# OR-behaviour on T; they DIFFERENTIATE only on graded peer confidence (see neutro.encode). The
# parametric forms divide by (1-x)/x or take log(x), so inputs are softened away from {0,1} by a
# tiny epsilon (a numerical safeguard; inactive on genuinely graded inputs).

_EPS = 1e-9


def _soft(x: float) -> float:
    """Clamp a membership away from the exact {0,1} corners for the parametric operators."""
    return _EPS if x <= _EPS else (1.0 - _EPS) if x >= 1.0 - _EPS else x


def svnn_einstein(zs: Sequence[SVNN], weights: Sequence[float] | None = None) -> SVNN:
    """Einstein weighted averaging: Einstein t-conorm on T, t-norm on I and F."""
    if not zs:
        raise ValueError("svnn_einstein requires at least one SVNN")
    w = normalize_weights(weights, len(zs))
    a = _wprod([1.0 + z.T for z in zs], w)
    b = _wprod([1.0 - z.T for z in zs], w)
    t = (a - b) / (a + b)
    pI, qI = _wprod([z.I for z in zs], w), _wprod([2.0 - z.I for z in zs], w)
    i = 2.0 * pI / (qI + pI)
    pF, qF = _wprod([z.F for z in zs], w), _wprod([2.0 - z.F for z in zs], w)
    f = 2.0 * pF / (qF + pF)
    return SVNN(_clamp01(t), _clamp01(i), _clamp01(f))


def svnn_hamacher(zs: Sequence[SVNN], weights: Sequence[float] | None = None,
                  *, gamma: float = 3.0) -> SVNN:
    """Hamacher weighted averaging (gamma>0). gamma=1 -> algebraic (=WAA); gamma=2 -> Einstein."""
    if not zs:
        raise ValueError("svnn_hamacher requires at least one SVNN")
    if gamma <= 0:
        raise ValueError(f"hamacher gamma must be > 0, got {gamma}")
    g = gamma
    w = normalize_weights(weights, len(zs))
    a = _wprod([1.0 + (g - 1.0) * z.T for z in zs], w)
    b = _wprod([1.0 - z.T for z in zs], w)
    t = (a - b) / (a + (g - 1.0) * b)
    pI = _wprod([z.I for z in zs], w)
    qI = _wprod([1.0 + (g - 1.0) * (1.0 - z.I) for z in zs], w)
    i = g * pI / (qI + (g - 1.0) * pI)
    pF = _wprod([z.F for z in zs], w)
    qF = _wprod([1.0 + (g - 1.0) * (1.0 - z.F) for z in zs], w)
    f = g * pF / (qF + (g - 1.0) * pF)
    return SVNN(_clamp01(t), _clamp01(i), _clamp01(f))


def svnn_dombi(zs: Sequence[SVNN], weights: Sequence[float] | None = None,
               *, gamma: float = 2.0) -> SVNN:
    """Dombi weighted averaging (gamma>=1; Wei et al. 2018). Larger gamma -> sharper aggregation."""
    if not zs:
        raise ValueError("svnn_dombi requires at least one SVNN")
    if gamma < 1.0:
        raise ValueError(f"dombi gamma must be >= 1, got {gamma}")
    g = gamma
    w = normalize_weights(weights, len(zs))
    sT = math.fsum(wj * (_soft(z.T) / (1.0 - _soft(z.T))) ** g for z, wj in zip(zs, w))
    sI = math.fsum(wj * ((1.0 - _soft(z.I)) / _soft(z.I)) ** g for z, wj in zip(zs, w))
    sF = math.fsum(wj * ((1.0 - _soft(z.F)) / _soft(z.F)) ** g for z, wj in zip(zs, w))
    t = 1.0 - 1.0 / (1.0 + sT ** (1.0 / g))
    i = 1.0 / (1.0 + sI ** (1.0 / g))
    f = 1.0 / (1.0 + sF ** (1.0 / g))
    return SVNN(_clamp01(t), _clamp01(i), _clamp01(f))


def svnn_aczel_alsina(zs: Sequence[SVNN], weights: Sequence[float] | None = None,
                      *, lam: float = 2.0) -> SVNN:
    """Aczel-Alsina weighted averaging (lambda>0). lambda=1 -> algebraic (=WAA)."""
    if not zs:
        raise ValueError("svnn_aczel_alsina requires at least one SVNN")
    if lam <= 0:
        raise ValueError(f"aczel-alsina lambda must be > 0, got {lam}")
    L = lam
    w = normalize_weights(weights, len(zs))
    sT = math.fsum(wj * (-math.log(1.0 - _soft(z.T))) ** L for z, wj in zip(zs, w))
    sI = math.fsum(wj * (-math.log(_soft(z.I))) ** L for z, wj in zip(zs, w))
    sF = math.fsum(wj * (-math.log(_soft(z.F))) ** L for z, wj in zip(zs, w))
    t = 1.0 - math.exp(-(sT ** (1.0 / L)))
    i = math.exp(-(sI ** (1.0 / L)))
    f = math.exp(-(sF ** (1.0 / L)))
    return SVNN(_clamp01(t), _clamp01(i), _clamp01(f))


def svnn_bonferroni(zs: Sequence[SVNN], weights: Sequence[float] | None = None,
                    *, p: float = 1.0, q: float = 1.0) -> SVNN:
    """SVNN Bonferroni mean (p,q>=0): captures interrelation between every ordered peer pair.

    BM = ( (1/(n(n-1))) (+)_{i!=j} z_i^p (x) z_j^q )^{1/(p+q)}, composed from the SVNN algebra in
    svnn.py. O(n^2); used at small/moderate R, excluded from the large-R scalability sweep.
    Unweighted (the pairwise interrelation, not the marginal weights).
    """
    if not zs:
        raise ValueError("svnn_bonferroni requires at least one SVNN")
    if p < 0 or q < 0:
        raise ValueError(f"bonferroni p,q must be >= 0, got p={p}, q={q}")
    n = len(zs)
    if n == 1:
        return zs[0]
    acc: SVNN | None = None
    for a in range(n):
        za_p = zs[a].power(p)
        for b in range(n):
            if a == b:
                continue
            term = za_p.otimes(zs[b].power(q))
            acc = term if acc is None else acc.oplus(term)
    mean = acc.scale(1.0 / (n * (n - 1)))
    res = mean.power(1.0 / (p + q))
    return SVNN(_clamp01(res.T), _clamp01(res.I), _clamp01(res.F))


#: Operator panel registry. Parametric members carry a representative default parameter; the
#: aggregate() dispatcher and the strategy factory look operators up by name here.
OPERATORS = {
    "waa": svnnwaa,            # weighted arithmetic (optimistic; submitted)
    "wga": svnnwga,            # weighted geometric (conservative; submitted)
    "einstein": svnn_einstein,
    "hamacher": svnn_hamacher,        # gamma=3
    "dombi": svnn_dombi,              # gamma=2
    "aczel_alsina": svnn_aczel_alsina,  # lambda=2
    "bonferroni": svnn_bonferroni,      # p=q=1 (pairwise interrelation)
}


def aggregate(method: str, zs: Sequence[SVNN], weights: Sequence[float] | None = None) -> SVNN:
    """Dispatch to an operator-panel member by name (defaults: see OPERATORS)."""
    try:
        op = OPERATORS[method]
    except KeyError:
        raise ValueError(
            f"unknown operator {method!r}; choose from {sorted(OPERATORS)}"
        ) from None
    return op(zs, weights)
