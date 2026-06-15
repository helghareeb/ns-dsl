"""The god-log: an append-only authoritative record of state-changing actions.

Written ONLY by the workload harness (never by a service under test), so it is a privileged
observer independent of any consensus strategy. Logical time is the append sequence number.
``truth.py`` reconstructs the true global state at any sequence point from this log -- the basis
for objectively scoring "consensus correctness" and "staleness".
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class LogEntry:
    seq: int
    key: str
    value: Any


class GodLog:
    def __init__(self) -> None:
        self._entries: list[LogEntry] = []
        self._seq = 0

    def append(self, key: str, value: Any) -> int:
        """Record an authoritative commit of ``key=value``; return its logical timestamp."""
        self._seq += 1
        self._entries.append(LogEntry(self._seq, key, value))
        return self._seq

    @property
    def now(self) -> int:
        return self._seq

    def entries(self) -> tuple[LogEntry, ...]:
        return tuple(self._entries)
