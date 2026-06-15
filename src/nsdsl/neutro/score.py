"""Deneutrosophy: convert an SVNN to a crisp score in [0, 1].

The 2020 chapter cites a score function (Eq. 2.3) whose printed form is OCR-corrupted and is
stated for a triangular/interval neutrosophic setting (the l, m, u parameters). For
single-valued neutrosophic numbers we use the standard, widely-used score function (Ye, 2014):

    s(z) = (2 + T - I - F) / 3      in [0, 1], higher = more "true/fresh".

A boolean accept decision compares the score against a tunable threshold tau (fixed per scenario
on a held-out calibration workload, then frozen -- see the methodology).
"""
from __future__ import annotations

from .svnn import SVNN


def score(z: SVNN) -> float:
    """Standard SVNN deneutrosophy score in [0, 1]."""
    return (2.0 + z.T - z.I - z.F) / 3.0


def decide(z: SVNN, threshold: float = 0.5) -> bool:
    """Accept (e.g. 'fresh enough to act on') iff score(z) >= threshold."""
    return score(z) >= threshold
