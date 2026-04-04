from typing import Callable

from spud.stage_six import ASTNode, ListLiteral
from spud_fmt.config import FmtConfig
from spud_fmt.formatter_protocol import FormatterDispatch


class ListLiteralFormatter:
    def __init__(self, config: FmtConfig, fmt: Callable[[], FormatterDispatch]):
        self._config = config
        self._fmt = fmt

    def format(self, node: ASTNode, depth: int) -> str:
        match node:
            case ListLiteral(elements=elements):
                separator = ", " if self._config.space_after_comma else ","
                formatted = [self._fmt().format_node(elem, depth) for elem in elements]
                return f"[{separator.join(formatted)}]"
