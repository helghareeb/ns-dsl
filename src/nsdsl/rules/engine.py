"""Evaluate a business rule against a fact set.

Facts is a mapping ``operand -> value``. A clause's right-hand ``value`` resolves to a fact when
it names one (e.g. "User Birthday"), otherwise it is treated as a literal (e.g. "Egypt", "3").
Clauses combine left-to-right by their connective (default "and"). Unknown operands make a
clause false rather than raising, so a partially-known fact set degrades safely.
"""
from __future__ import annotations

from typing import Any

from .models import Clause, Decision, RuleSpec
from .operators import COMPARATORS


def _resolve_value(token: str, facts: dict[str, Any]) -> Any:
    return facts[token] if token in facts else token


def eval_clause(clause: Clause, facts: dict[str, Any]) -> bool:
    if clause.operand not in facts:
        return False
    left = facts[clause.operand]
    right = _resolve_value(clause.value, facts)
    comparator = COMPARATORS.get(clause.operator)
    if comparator is None:
        raise ValueError(f"unsupported comparator {clause.operator!r}")
    try:
        return comparator(left, right)
    except ValueError:
        return False


def evaluate(rule: RuleSpec, facts: dict[str, Any]) -> Decision:
    provenance: list[tuple[Clause, bool]] = []
    result: bool | None = None
    for clause in rule.clauses:
        p = eval_clause(clause, facts)
        provenance.append((clause, p))
        if result is None:
            result = p
        elif clause.connective == "or":
            result = result or p
        elif clause.connective == "not":
            result = result and (not p)
        else:  # "and" (and the default for a missing connective)
            result = result and p
    return Decision(
        rule_id=rule.guid,
        title=rule.title,
        fired=bool(result),
        provenance=tuple(provenance),
    )
