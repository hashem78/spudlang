from typing import Callable

from spud.stage_six import ASTNode, IfElse
from spud_fmt.config import FmtConfig
from spud_fmt.formatter_protocol import FormatterDispatch
from spud_fmt.formatters.body_fmt import format_body


class IfElseFormatter:
    def __init__(self, config: FmtConfig, fmt: Callable[[], FormatterDispatch]):
        self._config = config
        self._fmt = fmt

    def format(self, node: ASTNode, depth: int) -> str:
        match node:
            case IfElse(branches=branches, else_body=else_body):
                indent = " " * (depth * self._config.indent_size)
                parts: list[str] = []

                for i, branch in enumerate(branches):
                    keyword = "if" if i == 0 else "elif"
                    condition = self._fmt().format_node(branch.condition, depth)
                    header = f"{indent}{keyword} {condition}"
                    body_lines = format_body(branch.body, depth + 1, self._config, self._fmt)
                    parts.append(f"{header}\n{body_lines}")

                if else_body:
                    header = f"{indent}else"
                    body_lines = format_body(else_body, depth + 1, self._config, self._fmt)
                    parts.append(f"{header}\n{body_lines}")

                return "\n".join(parts)
