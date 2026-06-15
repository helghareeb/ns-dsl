"""Single-Valued Neutrosophic Number (SVNN) and its algebra.

An SVNN is a triple (T, I, F) with T, I, F in [0, 1], representing truth-, indeterminacy-,
and falsity-membership independently (Smarandache; Wang et al.). The standard SVNN operations
below (Ye; Jana & Pal, 2019) are the per-term building blocks of the weighted aggregation
operators in ``operators.py`` -- implemented once here and composed there.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

_TOL = 1e-9


def _check_unit(name: str, x: float) -> None:
    if not (0.0 - _TOL <= x <= 1.0 + _TOL):
        raise ValueError(f"{name}={x!r} out of range; SVNN components must lie in [0, 1]")


@dataclass(frozen=True, slots=True)
class SVNN:
    """A single-valued neutrosophic number (T, I, F), each component in [0, 1]."""

    T: float
    I: float
    F: float

    def __post_init__(self) -> None:
        _check_unit("T", self.T)
        _check_unit("I", self.I)
        _check_unit("F", self.F)

    # --- standard SVNN algebra (operands assumed valid) -----------------------

    def complement(self) -> SVNN:
        """Neutrosophic complement: (F, 1 - I, T)."""
        return SVNN(self.F, 1.0 - self.I, self.T)

    def oplus(self, other: SVNN) -> SVNN:
        """Addition: (T1+T2 - T1*T2, I1*I2, F1*F2)."""
        return SVNN(
            self.T + other.T - self.T * other.T,
            self.I * other.I,
            self.F * other.F,
        )

    def otimes(self, other: SVNN) -> SVNN:
        """Multiplication: (T1*T2, I1+I2 - I1*I2, F1+F2 - F1*F2)."""
        return SVNN(
            self.T * other.T,
            self.I + other.I - self.I * other.I,
            self.F + other.F - self.F * other.F,
        )

    def scale(self, w: float) -> SVNN:
        """Scalar multiplication w * z = (1 - (1-T)^w, I^w, F^w), for w >= 0.

        This is the per-term of SVNNWAA.
        """
        if w < 0:
            raise ValueError(f"scale weight must be >= 0, got {w}")
        return SVNN(
            1.0 - (1.0 - self.T) ** w,
            self.I ** w,
            self.F ** w,
        )

    def power(self, w: float) -> SVNN:
        """Exponentiation z ^ w = (T^w, 1 - (1-I)^w, 1 - (1-F)^w), for w >= 0.

        This is the per-term of SVNNWGA.
        """
        if w < 0:
            raise ValueError(f"power weight must be >= 0, got {w}")
        return SVNN(
            self.T ** w,
            1.0 - (1.0 - self.I) ** w,
            1.0 - (1.0 - self.F) ** w,
        )

    # --- comparison / display -------------------------------------------------

    def almost_equal(self, other: SVNN, tol: float = 1e-9) -> bool:
        return (
            math.isclose(self.T, other.T, abs_tol=tol)
            and math.isclose(self.I, other.I, abs_tol=tol)
            and math.isclose(self.F, other.F, abs_tol=tol)
        )

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.T, self.I, self.F)

    def __str__(self) -> str:
        return f"({self.T:.4g},{self.I:.4g},{self.F:.4g})"
