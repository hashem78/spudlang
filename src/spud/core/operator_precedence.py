"""Operator precedence table shared across parser and formatter.

Levels are ordered from lowest (1) to highest binding strength.
Higher number = binds tighter. Operators at the same level have
equal precedence.

The ``max_applications`` field controls associativity:
- ``None`` means left-associative (unlimited chaining)
- ``1`` means non-associative (comparison operators)
"""

from spud.stage_five.stage_five_token_type import StageFiveTokenType as T

LEVELS: list[tuple[set[T], int | None]] = [
    ({T.LOGICAL_OR}, None),
    ({T.LOGICAL_AND}, None),
    ({T.EQUALS, T.NOT_EQUALS, T.LESS_THAN, T.GREATER_THAN, T.LESS_THAN_OR_EQUAL, T.GREATER_THAN_OR_EQUAL}, 1),
    ({T.PLUS, T.MINUS}, None),
    ({T.MULTIPLY, T.DIVIDE, T.MODULO}, None),
]

UNARY_PREFIX_OPS = {T.MINUS, T.PLUS}

OPERATOR_PRECEDENCE: dict[str, int] = {}
for level, (ops, _) in enumerate(LEVELS, start=1):
    for op in ops:
        OPERATOR_PRECEDENCE[op.value] = level

NON_ASSOCIATIVE_OPS: set[str] = set()
for ops, max_apps in LEVELS:
    if max_apps == 1:
        for op in ops:
            NON_ASSOCIATIVE_OPS.add(op.value)
