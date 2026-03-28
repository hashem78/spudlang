from typing import Callable

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.function_call import FunctionCall
from spud_fmt.config import FmtConfig
from spud_fmt.formatter_protocol import FormatterDispatch


class FunctionCallFormatter:
    def __init__(self, config: FmtConfig, fmt: Callable[[], FormatterDispatch]):
        self._config = config
        self._fmt = fmt

    def format(self, node: ASTNode, depth: int) -> str:
        assert isinstance(node, FunctionCall)
        formatted_args = [self._fmt().format_node(arg, depth) for arg in node.args]
        separator = ", " if self._config.space_after_comma else ","
        return f"{node.callee.name}({separator.join(formatted_args)})"
