"""Listener realization of "logs-as-DSL" (chapter Listing 2.5, Fig 2.7).

The chapter's central claim is that microservice logs are a DSL whose parse tree (Fig 2.6/2.7)
is walked by auto-generated *listeners* to drive behavior. This module provides a concrete
``JSONListener`` subclass that walks a neutrosophic event parse tree and collects each cart
item's ``(T,I,F)`` status annotation -- exactly the enrichment Fig 2.7 depicts. It is the
listener counterpart to the visitor-based extraction in ``event_parser.py``.
"""
from __future__ import annotations

import json

from antlr4 import ParseTreeWalker

from ..neutro import SVNN, parse_status
from .event_parser import parse_to_tree
from .generated.JSONListener import JSONListener
from .generated.JSONParser import JSONParser


class CartStatusListener(JSONListener):
    """Collect the neutrosophic status of each cart item as the tree is walked."""

    def __init__(self) -> None:
        self.statuses: list[SVNN] = []

    def enterPair(self, ctx: JSONParser.PairContext) -> None:  # noqa: N802
        key = json.loads(ctx.STRING().getText())
        value_ctx = ctx.value()
        if key == "status" and value_ctx.STRING() is not None:
            self.statuses.append(parse_status(json.loads(value_ctx.STRING().getText())))


def collect_statuses(text: str) -> list[SVNN]:
    """Walk the event's parse tree with a listener and return the SVNN status of each item."""
    _, tree = parse_to_tree(text)
    listener = CartStatusListener()
    ParseTreeWalker().walk(listener, tree)
    return listener.statuses
