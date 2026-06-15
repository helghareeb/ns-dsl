"""Scenario 1 -- personalized dynamic pricing, end-to-end over the in-process bus."""
from __future__ import annotations

from nsdsl.bus import InProcessBus
from services.products.logic import ProductsService
from services.users.logic import UserProfile, UsersService


def _wire():
    bus = InProcessBus()
    users = UsersService(bus)
    users.add_user(UserProfile("u_gold", loyalty="gold", birthday="1990-06-23", country="Egypt"))
    users.add_user(UserProfile("u_std", loyalty="standard", country="Egypt"))
    products = ProductsService(bus)
    products.add_product("p1", 100.0)
    return products


def test_gold_user_gets_personalized_discount():
    products = _wire()
    assert products.price_for("u_gold", "p1") == 90.0   # 10% loyalty discount applied
    assert products.price_for("u_std", "p1") == 100.0   # no discount


def test_unknown_user_pays_base_price():
    products = _wire()
    assert products.price_for("nobody", "p1") == 100.0
