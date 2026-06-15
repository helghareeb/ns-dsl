"""In-process event bus for unit tests and the single-node case study."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from .base import Handler, Responder


class NoResponderError(KeyError):
    """Raised when a request targets a topic with no registered responder."""


class InProcessBus:
    """Synchronous in-memory pub/sub + request/reply. Deterministic for testing."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Handler]] = defaultdict(list)
        self._responders: dict[str, Responder] = {}

    def publish(self, topic: str, message: Any) -> None:
        for handler in list(self._subscribers.get(topic, ())):
            handler(message)

    def subscribe(self, topic: str, handler: Handler) -> None:
        self._subscribers[topic].append(handler)

    def register_responder(self, topic: str, responder: Responder) -> None:
        if topic in self._responders:
            raise ValueError(f"responder already registered for topic {topic!r}")
        self._responders[topic] = responder

    def request(self, topic: str, payload: Any) -> Any:
        try:
            responder = self._responders[topic]
        except KeyError as exc:
            raise NoResponderError(topic) from exc
        return responder(payload)
