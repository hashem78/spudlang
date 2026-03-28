from typing import Callable

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.binding import Binding
from spud.stage_six.for_loop import ForLoop
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.if_else import IfElse
from spud_fmt.config import FmtConfig
from spud_fmt.formatter_protocol import FormatterDispatch


def is_block_node(node: ASTNode) -> bool:
    match node:
        case Binding(value=FunctionDef()):
            return True
        case IfElse() | ForLoop():
            return True
        case _:
            return False


def format_body(body: list[ASTNode], depth: int, config: FmtConfig, fmt: Callable[[], FormatterDispatch]) -> str:
    """Format a list of statements as an indented block."""
    indent = " " * (depth * config.indent_size)
    lines: list[str] = []
    prev_had_block = False

    for i, node in enumerate(body):
        has_block = is_block_node(node)
        if i > 0 and config.blank_lines_around_blocks and (has_block or prev_had_block):
            lines.append("")

        match node:
            case Binding() | IfElse() | ForLoop() | FunctionDef():
                lines.append(fmt().format_node(node, depth))
            case _:
                lines.append(f"{indent}{fmt().format_node(node, depth)}")

        prev_had_block = has_block

    return "\n".join(lines)
