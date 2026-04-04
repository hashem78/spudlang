from typing import Callable

from spud.core import NON_ASSOCIATIVE_OPS, NON_COMMUTATIVE_OPS, OPERATOR_PRECEDENCE
from spud.stage_six import ASTNode, BinaryOp
from spud_fmt.config import FmtConfig
from spud_fmt.formatter_protocol import FormatterDispatch


class BinaryOpFormatter:
    def __init__(self, config: FmtConfig, fmt: Callable[[], FormatterDispatch]):
        self._config = config
        self._fmt = fmt

    def format(self, node: ASTNode, depth: int) -> str:
        match node:
            case BinaryOp(left=left, operator=operator, right=right):
                left_str = self._format_operand(left, operator, is_right=False, depth=depth)
                right_str = self._format_operand(right, operator, is_right=True, depth=depth)
                if self._config.spaces_around_operators:
                    return f"{left_str} {operator} {right_str}"
                return f"{left_str}{operator}{right_str}"

    def _format_operand(self, operand: ASTNode, parent_op: str, is_right: bool, depth: int) -> str:
        formatted = self._fmt().format_node(operand, depth)
        if not isinstance(operand, BinaryOp):
            return formatted

        parent_prec = OPERATOR_PRECEDENCE.get(parent_op, 0)
        child_prec = OPERATOR_PRECEDENCE.get(operand.operator, 0)

        needs_parens = child_prec < parent_prec
        if is_right and child_prec == parent_prec:
            if (
                parent_op in NON_ASSOCIATIVE_OPS
                or parent_op in NON_COMMUTATIVE_OPS
                or operand.operator in NON_COMMUTATIVE_OPS
            ):
                needs_parens = True

        return f"({formatted})" if needs_parens else formatted
