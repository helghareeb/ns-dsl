"""DSL parsing of the chapter's event listings (2.1 plain, 2.2 neutrosophic)."""
from __future__ import annotations

import pytest

from nsdsl.dsl import DSLSyntaxError, collect_statuses, parse_event, to_python
from nsdsl.neutro.states import CACHED, DEFAULT, PERSISTED

# Listing 2.1 -- plain e-Commerce event (cartItems as an object, no status).
LISTING_2_1 = """
{"guid" : "abc123xyz",
 "description" : "Purchase Operation Pending",
 "cartItems" : {"book":"Microservices and DSLs","chapter":"Enterprise Integration"},
 "nodeID" : "1234"
}
"""

# Listing 2.2 -- neutrosophic event (cartItems as an array; book persisted, chapter cached).
LISTING_2_2 = """
{
  "guid" : "abc123xyz",
  "description" : "Purchase Operation Pending",
  "cartItems" : [
    {"book":"Microservices and DSLs", "status": "(1,0,0)"},
    {"chapter":"Enterprise Integration", "status": "(0,1,0)"}
  ],
  "nodeID" : "1234"
}
"""


def test_to_python_roundtrips_via_antlr():
    obj = to_python(LISTING_2_1)
    assert obj["guid"] == "abc123xyz"
    assert obj["cartItems"]["book"] == "Microservices and DSLs"


def test_parse_listing_2_1_defaults_to_unseen_status():
    ev = parse_event(LISTING_2_1)
    assert ev.guid == "abc123xyz"
    assert ev.node_id == "1234"
    assert {ci.key for ci in ev.cart_items} == {"book", "chapter"}
    # No status in Listing 2.1 -> DEFAULT (0,0,1), the corrected "never seen" state.
    assert all(ci.status == DEFAULT for ci in ev.cart_items)


def test_parse_listing_2_2_annotates_neutrosophic_status():
    ev = parse_event(LISTING_2_2)
    by_key = {ci.key: ci for ci in ev.cart_items}
    assert by_key["book"].title == "Microservices and DSLs"
    assert by_key["book"].status == PERSISTED   # (1,0,0) committed
    assert by_key["chapter"].status == CACHED   # (0,1,0) cache-only


def test_listener_collects_statuses_in_order():
    # The listener counterpart (Fig 2.7) walks the tree and yields each item's status.
    assert collect_statuses(LISTING_2_2) == [PERSISTED, CACHED]
    assert collect_statuses(LISTING_2_1) == []  # no status annotations present


def test_numbers_and_keywords_decode():
    assert to_python('{"n": -3.5, "e": 1e3, "ok": true, "no": false, "nil": null}') == {
        "n": -3.5, "e": 1000.0, "ok": True, "no": False, "nil": None,
    }


def test_syntax_error_raises():
    with pytest.raises(DSLSyntaxError):
        parse_event('{"guid": }')
