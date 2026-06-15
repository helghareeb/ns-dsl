"""JSON rules engine: Business Rule 001 (Listing 2.3) firing logic."""
from __future__ import annotations

from nsdsl.rules import collect_operator_tags, evaluate, load_rule_text

# Listing 2.3 -- "Special Discount if Delivery is Egypt, items > 3, and Today is User Birthday".
BUSINESS_RULE_001 = """
{"guid" : "BR000001",
 "Title" : "Business Rule 001",
 "Date" : "23/06/2019",
 "description" : "Special Discount on Purchases if Delivery Country is Egypt, Items greater than 3, and Today is User Birthday",
 "rule" : [
   { "Today" : { "equal" : "User Birthday" } },
   { "and" : { "items in cart" : { "gt" : "3" } } },
   { "and" : { "Delivery" : { "equal" : "Egypt" } } }
 ]
}
"""


def _facts(today="2019-06-23", birthday="2019-06-23", items=5, delivery="Egypt"):
    return {
        "Today": today,
        "User Birthday": birthday,
        "items in cart": items,
        "Delivery": delivery,
    }


def test_rule_loads_three_clauses():
    rule = load_rule_text(BUSINESS_RULE_001)
    assert rule.guid == "BR000001"
    assert len(rule.clauses) == 3
    assert rule.clauses[0].connective is None
    assert rule.clauses[1].connective == "and"
    assert (rule.clauses[1].operand, rule.clauses[1].operator, rule.clauses[1].value) == (
        "items in cart", "gt", "3",
    )


def test_rule_fires_when_all_clauses_hold():
    rule = load_rule_text(BUSINESS_RULE_001)
    assert evaluate(rule, _facts()).fired is True


def test_rule_does_not_fire_when_items_too_few():
    rule = load_rule_text(BUSINESS_RULE_001)
    assert evaluate(rule, _facts(items=2)).fired is False


def test_rule_does_not_fire_when_country_differs():
    rule = load_rule_text(BUSINESS_RULE_001)
    assert evaluate(rule, _facts(delivery="Sudan")).fired is False


def test_rule_does_not_fire_when_not_birthday():
    rule = load_rule_text(BUSINESS_RULE_001)
    assert evaluate(rule, _facts(today="2019-06-24")).fired is False


def test_missing_operand_makes_clause_false_not_error():
    rule = load_rule_text(BUSINESS_RULE_001)
    facts = _facts()
    del facts["Delivery"]
    assert evaluate(rule, facts).fired is False


def test_listener_recognizes_operator_tags_in_order():
    assert collect_operator_tags(BUSINESS_RULE_001) == ["equal", "and", "gt", "and", "equal"]


def test_provenance_records_each_clause_outcome():
    rule = load_rule_text(BUSINESS_RULE_001)
    decision = evaluate(rule, _facts(items=2))
    outcomes = [fired for _clause, fired in decision.provenance]
    assert outcomes == [True, False, True]   # birthday ok, items fail, delivery ok
