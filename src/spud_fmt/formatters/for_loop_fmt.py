from typing import Callable

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.for_loop import ForLoop
from spud_fmt.config import FmtConfig
from spud_fmt.formatter_protocol import FormatterDispatch
from spud_fmt.formatters.body_fmt import format_body


class ForLoopFormatter:
    def __init__(self, config: FmtConfig, fmt: Callable[[], FormatterDispatch]):
        self._config = config
        self._fmt = fmt

    def format(self, node: ASTNode, depth: int) -> str:
        assert isinstance(node, ForLoop)
        indent = " " * (depth * self._config.indent_size)
        iterable_str = self._fmt().format_node(node.iterable, depth)
        header = f"{indent}for {node.variable.name} in {iterable_str}"
        body_lines = format_body(node.body, depth + 1, self._config, self._fmt)
        return f"{header}\n{body_lines}"
