"""S3 clone catch-up: rebuild a fresh replica's state by replaying the logs-as-DSL stream.

The chapter's Scenario 3 ("White Friday" load spike): a newly cloned stateful container starts
in DEFAULT = (0,0,1) for everything and must catch up to the global state. Because microservice
event logs ARE the DSL, the new replica replays them through the event parser, transitioning each
item DEFAULT -> CACHED -> PERSISTED, until its state matches the established peers / oracle.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..dsl import parse_event
from ..neutro.states import CACHED, PERSISTED
from ..state_store import NeutrosophicStateStore


@dataclass(frozen=True, slots=True)
class CatchUpResult:
    events_replayed: int
    keys_recovered: int


def item_key(guid: str, item: str) -> str:
    return f"{guid}:{item}"


def apply_event(store: NeutrosophicStateStore, event_text: str) -> set[str]:
    """Apply one DSL event log to ``store``; return the keys it touched."""
    event = parse_event(event_text)
    touched: set[str] = set()
    for it in event.cart_items:
        key = item_key(event.guid, it.key)
        if it.status == PERSISTED:
            store.persist(key, it.title)
        elif it.status == CACHED:
            store.write_cache(key, it.title)
        else:
            continue
        touched.add(key)
    return touched


def replay(store: NeutrosophicStateStore, event_texts: Sequence[str]) -> CatchUpResult:
    """Replay an ordered event-log stream into ``store`` (a fresh replica catching up)."""
    recovered: set[str] = set()
    for text in event_texts:
        recovered |= apply_event(store, text)
    return CatchUpResult(events_replayed=len(event_texts), keys_recovered=len(recovered))
