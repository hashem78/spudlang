from typing import Callable

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.list_literal import ListLiteral
from spud_fmt.config import FmtConfig
from spud_fmt.formatter_protocol import FormatterDispatch


class ListLiteralFormatter:
    def __init__(self, config: FmtConfig, fmt: Callable[[], FormatterDispatch]):
        self._config = config
        self._fmt = fmt

    def format(self, node: ASTNode, depth: int) -> str:
        assert isinstance(node, ListLiteral)
        separator = ", " if self._config.space_after_comma else ","
        elements = [self._fmt().format_node(elem, depth) for elem in node.elements]
        return f"[{separator.join(elements)}]"
