from typing import Callable

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.binary_op import BinaryOp
from spud.stage_six.unary_op import UnaryOp
from spud_fmt.config import FmtConfig
from spud_fmt.formatter_protocol import FormatterDispatch


class UnaryOpFormatter:
    def __init__(self, config: FmtConfig, fmt: Callable[[], FormatterDispatch]):
        self._config = config
        self._fmt = fmt

    def format(self, node: ASTNode, depth: int) -> str:
        assert isinstance(node, UnaryOp)
        has_plus = False
        neg_count = 0
        inner: ASTNode = node
        while isinstance(inner, UnaryOp):
            if inner.operator == "-":
                neg_count += 1
            elif inner.operator == "+":
                has_plus = True
            inner = inner.operand
        operand = self._fmt().format_node(inner, depth)
        if neg_count % 2 == 1:
            if isinstance(inner, BinaryOp):
                return f"-({operand})"
            return f"-{operand}"
        if has_plus and not self._config.collapse_unary_plus:
            if isinstance(inner, BinaryOp):
                return f"+({operand})"
            return f"+{operand}"
        return operand
