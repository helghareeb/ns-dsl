"""Products microservice logic (owns the catalog; computes personalized prices -- Scenario 1).

Pricing needs cross-service data (the user's loyalty tier from the users service). The chapter's
problem: that data must be integrated without a central authority and without hard-coding the
rule. Here the discount is expressed as a JSON business rule (``rules/pricing.rules.json``) and
the user facts are fetched over the bus, so the rule can change without redeploying the service.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from nsdsl.bus import EventBus
from nsdsl.rules import RuleSpec, evaluate, load_rule_text
from nsdsl.state_store import NeutrosophicStateStore

_RULE_PATH = Path(__file__).parent / "rules" / "pricing.rules.json"
GOLD_DISCOUNT = 0.10


@dataclass
class ProductsService:
    bus: EventBus
    store: NeutrosophicStateStore = field(default_factory=NeutrosophicStateStore)
    pricing_rule: RuleSpec = field(init=False)

    def __post_init__(self) -> None:
        self.pricing_rule = load_rule_text(_RULE_PATH.read_text(encoding="utf-8"))

    def add_product(self, product_id: str, base_price: float) -> None:
        self.store.persist(f"product:{product_id}", float(base_price))

    def base_price(self, product_id: str) -> float:
        stored = self.store.get(f"product:{product_id}")
        if not stored.present:
            raise KeyError(f"unknown product {product_id!r}")
        return float(stored.value)

    def price_for(self, user_id: str, product_id: str) -> float:
        """Personalized price = base price with any business-rule discount applied."""
        base = self.base_price(product_id)
        facts = self.bus.request("users.facts", user_id)
        decision = evaluate(self.pricing_rule, facts)
        discount = GOLD_DISCOUNT if decision.fired else 0.0
        return round(base * (1.0 - discount), 2)
