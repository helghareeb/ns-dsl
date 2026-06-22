"""Deneutrosophy: convert an SVNN to a crisp score in [0, 1] (Axis-A' score panel).

The 2020 chapter cites a score function (Eq. 2.3) whose printed form is OCR-corrupted and is
stated for a triangular/interval neutrosophic setting. For single-valued neutrosophic numbers the
standard, widely-used score function (Ye, 2014) is the default:

    standard(z) = (2 + T - I - F) / 3      in [0, 1], higher = more "true/fresh".

To audit whether the freshness-decision result depends on this particular deneutrosophy choice, a
panel of alternative scores is provided and compared as a robustness ablation. Every member maps an
SVNN to [0, 1] with higher = more true/fresh, so it drops into the same accept-iff-score>=tau gate.
"""
from __future__ import annotations

import math

from .svnn import SVNN

_EPS = 1e-12


def standard(z: SVNN) -> float:
    """Ye (2014) score: (2 + T - I - F) / 3. Treats indeterminacy and falsity symmetrically."""
    return (2.0 + z.T - z.I - z.F) / 3.0


def accuracy(z: SVNN) -> float:
    """Accuracy-degree score (Nancy & Garg, 2016): (1 + T - F) / 2. Ignores indeterminacy."""
    return (1.0 + z.T - z.F) / 2.0


def cosine(z: SVNN) -> float:
    """Ye (2014) cosine measure to the truth ideal (1,0,0): T / sqrt(T^2 + I^2 + F^2)."""
    norm = math.sqrt(z.T * z.T + z.I * z.I + z.F * z.F)
    return 0.0 if norm < _EPS else z.T / norm


def truth_weighted(z: SVNN) -> float:
    """Truth-dominant score: (3T + (1-I) + (1-F)) / 5. Penalises indeterminacy/falsity, demands
    more truth to clear a threshold (a stricter deneutrosophy than the standard score)."""
    return (3.0 * z.T + (1.0 - z.I) + (1.0 - z.F)) / 5.0


#: Deneutrosophy score panel. The default 'standard' reproduces the submitted decision exactly.
SCORES = {
    "standard": standard,        # Ye 2014 (submitted)
    "accuracy": accuracy,        # Nancy & Garg 2016
    "cosine": cosine,            # Ye 2014 cosine measure
    "truth_weighted": truth_weighted,
}


def score(z: SVNN, fn: str = "standard") -> float:
    """Deneutrosophy score in [0, 1] via panel member ``fn`` (default: Ye 2014 standard)."""
    try:
        f = SCORES[fn]
    except KeyError:
        raise ValueError(f"unknown score {fn!r}; choose from {sorted(SCORES)}") from None
    return f(z)


def decide(z: SVNN, threshold: float = 0.5, fn: str = "standard") -> bool:
    """Accept (e.g. 'fresh enough to act on') iff score(z, fn) >= threshold."""
    return score(z, fn) >= threshold
