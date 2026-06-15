"""Operator semantics for the JSON rules engine (chapter section 2.8.3.1 operator tag set)."""
from __future__ import annotations

from typing import Any


def _as_number(x: Any) -> float | None:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def op_equal(left: Any, right: Any) -> bool:
    """Equality; numeric when both sides parse as numbers, else string-insensitive compare."""
    ln, rn = _as_number(left), _as_number(right)
    if ln is not None and rn is not None:
        return ln == rn
    return str(left).strip().casefold() == str(right).strip().casefold()


def op_gt(left: Any, right: Any) -> bool:
    ln, rn = _as_number(left), _as_number(right)
    if ln is None or rn is None:
        raise ValueError(f"gt requires numeric operands, got {left!r}, {right!r}")
    return ln > rn


def op_lt(left: Any, right: Any) -> bool:
    ln, rn = _as_number(left), _as_number(right)
    if ln is None or rn is None:
        raise ValueError(f"lt requires numeric operands, got {left!r}, {right!r}")
    return ln < rn


# Comparison operators: (left, right) -> bool.
COMPARATORS = {
    "equal": op_equal,
    "gt": op_gt,
    "lt": op_lt,
}

# Arithmetic operators: (left, right) -> number. Provided for completeness of the tag set.
ARITHMETIC = {
    "add": lambda a, b: float(a) + float(b),
    "sub": lambda a, b: float(a) - float(b),
    "multiply": lambda a, b: float(a) * float(b),
    "divide": lambda a, b: float(a) / float(b),
    "modulo": lambda a, b: float(a) % float(b),
}
