"""Per-service local state store that tags each value with its neutrosophic status.

Models the chapter's caching layer (section 2.8.2): a value is either persisted to the database
(T=PERSISTED), held in cache only and not yet persisted (I=CACHED), or absent (F=DEFAULT). This
is the application-level mechanism that makes dirty reads / dirty writes observable -- a read
returns both the value and its ``(T,I,F)`` provenance, which the consensus layer aggregates.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .neutro import CACHED, DEFAULT, PERSISTED, SVNN


@dataclass(frozen=True, slots=True)
class StoredValue:
    value: Any
    status: SVNN

    @property
    def present(self) -> bool:
        return self.status is not DEFAULT


class NeutrosophicStateStore:
    """A two-tier (cache / database) key-value store with neutrosophic status tagging."""

    def __init__(self) -> None:
        self._db: dict[str, Any] = {}
        self._cache: dict[str, Any] = {}

    def write_cache(self, key: str, value: Any) -> None:
        """Write to cache only (unconfirmed) -> status becomes CACHED on read."""
        self._cache[key] = value

    def persist(self, key: str, value: Any) -> None:
        """Commit to the database -> status becomes PERSISTED; drops any stale cache entry."""
        self._db[key] = value
        self._cache.pop(key, None)

    def flush(self, key: str) -> bool:
        """Promote a cache-only value to the database. Returns False if nothing was cached."""
        if key not in self._cache:
            return False
        self._db[key] = self._cache.pop(key)
        return True

    def get(self, key: str) -> StoredValue:
        if key in self._db:
            return StoredValue(self._db[key], PERSISTED)
        if key in self._cache:
            return StoredValue(self._cache[key], CACHED)
        return StoredValue(None, DEFAULT)

    def status(self, key: str) -> SVNN:
        return self.get(key).status
