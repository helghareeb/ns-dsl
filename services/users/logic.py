"""Users microservice logic (data sovereignty: owns user profiles).

Holds loyalty tier, birthday, and country per user, and answers cross-service fact requests over
the bus (topic ``users.facts``). Other services never read this store directly -- they ask via
the bus, honoring the chapter's data-sovereignty rule (section 2.2.1).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nsdsl.bus import EventBus
from nsdsl.state_store import NeutrosophicStateStore

FACTS_TOPIC = "users.facts"


@dataclass(frozen=True, slots=True)
class UserProfile:
    user_id: str
    loyalty: str = "standard"       # standard | silver | gold
    birthday: str = ""              # ISO date
    country: str = ""


@dataclass
class UsersService:
    bus: EventBus
    store: NeutrosophicStateStore = field(default_factory=NeutrosophicStateStore)

    def __post_init__(self) -> None:
        self.bus.register_responder(FACTS_TOPIC, self._on_facts_request)

    def add_user(self, profile: UserProfile) -> None:
        self.store.persist(f"user:{profile.user_id}", profile)

    def _on_facts_request(self, user_id: str) -> dict[str, Any]:
        stored = self.store.get(f"user:{user_id}")
        if not stored.present:
            return {}
        p: UserProfile = stored.value
        return {"loyalty": p.loyalty, "User Birthday": p.birthday, "country": p.country}
