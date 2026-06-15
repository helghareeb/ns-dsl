"""Domain models for the e-Commerce DSL events (chapter Listings 2.1 / 2.2)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..neutro import DEFAULT, SVNN, parse_status


@dataclass(frozen=True, slots=True)
class CartItem:
    """One item in a purchase event, with its neutrosophic persistence status."""

    key: str          # the content field name, e.g. "book" / "chapter"
    title: str        # the value, e.g. "Microservices and DSLs"
    status: SVNN = DEFAULT


@dataclass(frozen=True, slots=True)
class Event:
    """A parsed microservice event log treated as a DSL sentence."""

    guid: str
    description: str
    node_id: str
    cart_items: tuple[CartItem, ...] = ()
    raw: dict[str, Any] | None = None

    @staticmethod
    def from_dict(d: dict[str, Any]) -> Event:
        """Build an Event from the generic JSON dict, supporting both cart shapes:

        - Listing 2.1: ``"cartItems": {"book": "...", "chapter": "..."}`` (object, no status)
        - Listing 2.2: ``"cartItems": [{"book": "...", "status": "(1,0,0)"}, ...]`` (array w/ status)
        """
        items: list[CartItem] = []
        cart = d.get("cartItems")
        if isinstance(cart, dict):
            items = [CartItem(str(k), str(v), DEFAULT) for k, v in cart.items()]
        elif isinstance(cart, list):
            for elem in cart:
                if not isinstance(elem, dict):
                    continue
                status = DEFAULT
                content: tuple[str, str] | None = None
                for k, v in elem.items():
                    if k == "status":
                        status = parse_status(str(v))
                    else:
                        content = (str(k), str(v))
                if content is not None:
                    items.append(CartItem(content[0], content[1], status))
        return Event(
            guid=str(d.get("guid", "")),
            description=str(d.get("description", "")),
            node_id=str(d.get("nodeID", d.get("nodeId", ""))),
            cart_items=tuple(items),
            raw=d,
        )
