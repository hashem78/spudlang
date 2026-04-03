from typing import Callable

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.function_def import FunctionDef
from spud_fmt.config import FmtConfig
from spud_fmt.formatter_protocol import FormatterDispatch
from spud_fmt.formatters.body_fmt import format_body


class FunctionDefFormatter:
    def __init__(self, config: FmtConfig, fmt: Callable[[], FormatterDispatch]):
        self._config = config
        self._fmt = fmt

    def format(self, node: ASTNode, depth: int) -> str:
        match node:
            case FunctionDef(params=params, body=body):
                indent = " " * (depth * self._config.indent_size)
                param_names = [p.name for p in params]
                separator = ", " if self._config.space_after_comma else ","
                arrow = " =>" if self._config.spaces_around_fat_arrow else "=>"
                header = f"{indent}({separator.join(param_names)}){arrow}"
                body_lines = format_body(body, depth + 1, self._config, self._fmt)
                return f"{header}\n{body_lines}"
