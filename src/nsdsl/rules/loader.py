"""Load a business rule from JSON DSL text (Listing 2.3) into a ``RuleSpec``."""
from __future__ import annotations

from typing import Any

from ..dsl import to_python
from .models import Clause, RuleSpec
from .tags import CONNECTIVES


def _single_item(d: dict[str, Any]) -> tuple[str, Any]:
    if len(d) != 1:
        raise ValueError(f"expected a single-key object, got keys {list(d)}")
    (k, v), = d.items()
    return k, v


def parse_clause(clause: dict[str, Any]) -> Clause:
    """Parse one clause object into a ``Clause``.

    Forms:  {"Today": {"equal": "User Birthday"}}
            {"and": {"items in cart": {"gt": "3"}}}
    """
    top_key, top_val = _single_item(clause)
    if top_key in CONNECTIVES:
        connective = top_key
        operand, op_expr = _single_item(top_val)
    else:
        connective = None
        operand, op_expr = top_key, top_val
    if not isinstance(op_expr, dict):
        raise ValueError(f"clause operand {operand!r} must map to an operator object")
    operator, value = _single_item(op_expr)
    return Clause(operand=operand, operator=operator, value=str(value), connective=connective)


def load_rule(obj: dict[str, Any]) -> RuleSpec:
    """Build a ``RuleSpec`` from an already-parsed rule dict."""
    raw_clauses = obj.get("rule", [])
    if not isinstance(raw_clauses, list):
        raise ValueError("'rule' must be a list of clauses")
    clauses = tuple(parse_clause(c) for c in raw_clauses)
    return RuleSpec(
        guid=str(obj.get("guid", "")).strip(),
        title=str(obj.get("Title", obj.get("title", ""))),
        description=str(obj.get("description", "")),
        clauses=clauses,
    )


def load_rule_text(text: str) -> RuleSpec:
    """Parse rule DSL text via the ANTLR pipeline, then build a ``RuleSpec``."""
    obj = to_python(text)
    if not isinstance(obj, dict):
        raise ValueError("rule DSL must be a JSON object")
    return load_rule(obj)
