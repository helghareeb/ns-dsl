"""Listener over a rule parse tree (chapter Listing 2.5/2.6 mechanism).

Demonstrates that the auto-generated ANTLR listener drives the rules engine: as the rule's parse
tree is walked, operator tags are recognized in order. This is the faithful counterpart to the
chapter's ``BusinessRule_One(JSONListener)`` sketch.
"""
from __future__ import annotations

import json

from antlr4 import ParseTreeWalker

from ..dsl.event_parser import parse_to_tree
from ..dsl.generated.JSONListener import JSONListener
from ..dsl.generated.JSONParser import JSONParser
from .tags import OperatorTag

_OPERATOR_VALUES = {t.value for t in OperatorTag}


class OperatorTagListener(JSONListener):
    """Collect operator-tag keys in the order the rule tree is walked."""

    def __init__(self) -> None:
        self.tags: list[str] = []

    def enterPair(self, ctx: JSONParser.PairContext) -> None:  # noqa: N802
        key = json.loads(ctx.STRING().getText())
        if key in _OPERATOR_VALUES:
            self.tags.append(key)


def collect_operator_tags(text: str) -> list[str]:
    _, tree = parse_to_tree(text)
    listener = OperatorTagListener()
    ParseTreeWalker().walk(listener, tree)
    return listener.tags
