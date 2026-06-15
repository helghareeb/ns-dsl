"""Event-bus abstraction (the chapter's Fig 2.5 'simple event bus').

A ``Protocol`` so all microservice logic is transport-agnostic: an in-process implementation
backs unit tests and the single-node case study (M4); a Redis pub/sub implementation backs the
Dockerized testbed (M5). Both fire-and-forget publish/subscribe and synchronous request/reply
are supported -- request/reply models the cross-service fact lookups the scenarios need.
"""
from __future__ import annotations

from typing import Any, Callable, Protocol, runtime_checkable

Handler = Callable[[Any], None]
Responder = Callable[[Any], Any]


@runtime_checkable
class EventBus(Protocol):
    def publish(self, topic: str, message: Any) -> None:
        """Fire-and-forget broadcast to all subscribers of ``topic``."""
        ...

    def subscribe(self, topic: str, handler: Handler) -> None:
        """Register a fire-and-forget handler for ``topic``."""
        ...

    def register_responder(self, topic: str, responder: Responder) -> None:
        """Register the single responder that answers ``request`` calls on ``topic``."""
        ...

    def request(self, topic: str, payload: Any) -> Any:
        """Synchronous request/reply to the responder registered on ``topic``."""
        ...
