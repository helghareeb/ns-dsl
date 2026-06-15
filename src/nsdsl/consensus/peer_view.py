"""A peer's reportable view of an item's neutrosophic status."""
from __future__ import annotations

from dataclasses import dataclass

from ..neutro import SVNN
from ..state_store import NeutrosophicStateStore


@dataclass
class Peer:
    """A consensus participant backed by a local neutrosophic state store."""

    peer_id: str
    store: NeutrosophicStateStore

    def view(self, key: str) -> SVNN:
        """The peer's current ``(T,I,F)`` status for ``key`` (DEFAULT if it has never seen it)."""
        return self.store.status(key)
