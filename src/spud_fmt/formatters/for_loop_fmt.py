from typing import Callable

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.for_loop import ForLoop
from spud_fmt.config import FmtConfig
from spud_fmt.formatter_protocol import FormatterDispatch
from spud_fmt.formatters.body_fmt import format_body
from spud_fmt.formatters.type_fmt import format_type


class ForLoopFormatter:
    def __init__(self, config: FmtConfig, fmt: Callable[[], FormatterDispatch]):
        self._config = config
        self._fmt = fmt

    def format(self, node: ASTNode, depth: int) -> str:
        match node:
            case ForLoop(variable=variable, variable_type=variable_type, iterable=iterable, body=body):
                indent = " " * (depth * self._config.indent_size)
                type_str = format_type(variable_type)
                iterable_str = self._fmt().format_node(iterable, depth)
                header = f"{indent}for {variable.name} : {type_str} in {iterable_str}"
                body_lines = format_body(body, depth + 1, self._config, self._fmt)
                return f"{header}\n{body_lines}"
