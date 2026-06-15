"""Parse microservice event logs (the DSL) via the ANTLR JSON pipeline.

Realizes the chapter's Eq. 2.5:  chars -> LEXER -> tokens -> PARSER -> parse tree.
The structure is recovered from the ANTLR parse tree by the auto-generated visitor; scalar
tokens (strings/numbers) are decoded with the stdlib ``json`` module so escapes are handled
correctly. The resulting native object is mapped onto the domain models in ``models.py``.
"""
from __future__ import annotations

import json
from typing import Any

from antlr4 import CommonTokenStream, InputStream, ParserRuleContext
from antlr4.error.ErrorListener import ErrorListener

from .generated.JSONLexer import JSONLexer
from .generated.JSONParser import JSONParser
from .generated.JSONVisitor import JSONVisitor
from .models import Event


class DSLSyntaxError(ValueError):
    """Raised when the DSL input is not syntactically valid JSON per the grammar."""


class _RaisingErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offending_symbol, line, column, msg, e):  # noqa: N802
        raise DSLSyntaxError(f"line {line}:{column} {msg}")


class _JSONToPy(JSONVisitor):
    """Reconstruct a native Python value from the generic JSON parse tree."""

    def visitJson(self, ctx: JSONParser.JsonContext) -> Any:  # noqa: N802
        return self.visit(ctx.value())

    def visitObj(self, ctx: JSONParser.ObjContext) -> dict[str, Any]:  # noqa: N802
        return {
            json.loads(p.STRING().getText()): self.visit(p.value())
            for p in ctx.pair()
        }

    def visitArr(self, ctx: JSONParser.ArrContext) -> list[Any]:  # noqa: N802
        return [self.visit(v) for v in ctx.value()]

    def visitValue(self, ctx: JSONParser.ValueContext) -> Any:  # noqa: N802
        if ctx.STRING() is not None:
            return json.loads(ctx.STRING().getText())
        if ctx.NUMBER() is not None:
            return json.loads(ctx.NUMBER().getText())
        if ctx.obj() is not None:
            return self.visit(ctx.obj())
        if ctx.arr() is not None:
            return self.visit(ctx.arr())
        return {"true": True, "false": False, "null": None}[ctx.getText()]


def parse_to_tree(text: str) -> tuple[JSONParser, ParserRuleContext]:
    """Run lexer + parser; return (parser, parse tree). Raises ``DSLSyntaxError`` on bad input."""
    lexer = JSONLexer(InputStream(text))
    lexer.removeErrorListeners()
    lexer.addErrorListener(_RaisingErrorListener())
    parser = JSONParser(CommonTokenStream(lexer))
    parser.removeErrorListeners()
    parser.addErrorListener(_RaisingErrorListener())
    return parser, parser.json()


def to_python(text: str) -> Any:
    """Parse DSL text into a native Python object via the ANTLR pipeline."""
    _, tree = parse_to_tree(text)
    return _JSONToPy().visit(tree)


def parse_event(text: str) -> Event:
    """Parse an e-Commerce event log (Listing 2.1 / 2.2) into an annotated ``Event``."""
    obj = to_python(text)
    if not isinstance(obj, dict):
        raise DSLSyntaxError("event log must be a JSON object")
    return Event.from_dict(obj)
