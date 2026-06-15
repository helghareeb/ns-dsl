"""Reconstruct ground-truth global state from the god-log.

The true value of a key at logical time ``at`` is the value of its last commit with seq <= at.
A system's decision is *stale* iff it acted on a value different from the oracle's true value at
the time the decision was made.
"""
from __future__ import annotations

from typing import Any

from .god_log import GodLog


class Oracle:
    def __init__(self, log: GodLog) -> None:
        self.log = log

    def true_value(self, key: str, at: int | None = None) -> Any:
        at = self.log.now if at is None else at
        value: Any = None
        for entry in self.log.entries():
            if entry.seq > at:
                break
            if entry.key == key:
                value = entry.value
        return value

    def global_state(self, at: int | None = None) -> dict[str, Any]:
        at = self.log.now if at is None else at
        state: dict[str, Any] = {}
        for entry in self.log.entries():
            if entry.seq > at:
                break
            state[entry.key] = entry.value
        return state

    def is_stale(self, key: str, acted_value: Any, at: int | None = None) -> bool:
        """True if ``acted_value`` differs from the true value of ``key`` at time ``at``."""
        return acted_value != self.true_value(key, at)
