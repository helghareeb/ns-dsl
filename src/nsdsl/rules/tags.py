"""Business-rules DSL tag sets (chapter section 2.8.3.1, after Yin et al. [17]).

The chapter reformats Yin et al.'s service-oriented rules language from XML into JSON. These
enums document and validate the four tag sets the language recognizes.
"""
from __future__ import annotations

from enum import Enum


class LogicalTag(str, Enum):
    RULESET = "ruleset"
    RULE = "rule"
    WHEN = "when"
    THEN = "then"
    PARAM = "param"


class ServiceTag(str, Enum):
    SERVICE = "service"


class OperatorTag(str, Enum):
    OPT = "opt"
    AND = "and"
    OR = "or"
    NOT = "not"
    EQUAL = "equal"
    ADD = "add"
    SUB = "sub"
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    MODULO = "modulo"
    ADDEQUAL = "addequal"
    SUBEQUAL = "subequal"
    MULTIPLYEQUAL = "multiplyequal"
    DIVIDEEQUAL = "divideequal"
    MODULOEQUAL = "moduloequal"
    GT = "gt"
    LT = "lt"
    OPENPARENTHESI = "openparenthesi"
    CLOSEPARENTHESI = "closeparenthesi"


class EnvironmentalTag(str, Enum):
    PACKAGE = "package"


# Operator tags that combine clauses (logical connectives).
CONNECTIVES = {OperatorTag.AND.value, OperatorTag.OR.value, OperatorTag.NOT.value}

# Operator tags that compare two operands and yield a boolean.
COMPARATORS = {OperatorTag.EQUAL.value, OperatorTag.GT.value, OperatorTag.LT.value}
