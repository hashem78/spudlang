"""Derived lookup tables built from the operator definitions.

All tables are computed from ``OPERATORS`` in ``spud.core.operators``.
"""

from spud.core.operator_info import Associativity, OperatorKind
from spud.core.operators import OPERATORS
from spud.stage_five.stage_five_token_type import StageFiveTokenType as T

LEVELS: list[tuple[set[T], int | None]] = []
_level_map: dict[int, tuple[set[T], int | None]] = {}
for _op in OPERATORS:
    if _op.kind != OperatorKind.BINARY:
        continue
    _max_apps = 1 if _op.associativity == Associativity.NONE else None
    if _op.precedence not in _level_map:
        _level_map[_op.precedence] = (set(), _max_apps)
    _level_map[_op.precedence][0].add(_op.token)
LEVELS = [_level_map[p] for p in sorted(_level_map)]

UNARY_PREFIX_OPS: set[T] = {op.token for op in OPERATORS if op.kind == OperatorKind.UNARY_PREFIX}

OPERATOR_PRECEDENCE: dict[str, int] = {
    op.token.value: op.precedence for op in OPERATORS if op.kind == OperatorKind.BINARY
}

NON_ASSOCIATIVE_OPS: set[str] = {op.token.value for op in OPERATORS if op.associativity == Associativity.NONE}

NON_COMMUTATIVE_OPS: set[str] = {op.token.value for op in OPERATORS if not op.commutative}
