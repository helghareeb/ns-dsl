"""Rule model: a business rule is an ordered list of clauses joined by logical connectives.

Mirrors the chapter's Listing 2.3 structure. Each clause is ``{operand: {operator: value}}``,
optionally wrapped by a connective key (``and`` / ``or`` / ``not``) for clauses after the first.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Clause:
    operand: str
    operator: str
    value: str
    connective: str | None = None   # None for the first clause; "and"/"or"/"not" thereafter


@dataclass(frozen=True, slots=True)
class RuleSpec:
    guid: str
    title: str
    description: str
    clauses: tuple[Clause, ...]


@dataclass(frozen=True, slots=True)
class Decision:
    """Outcome of evaluating a rule against a fact set, with per-clause provenance."""

    rule_id: str
    title: str
    fired: bool
    provenance: tuple[tuple[Clause, bool], ...] = field(default=())
