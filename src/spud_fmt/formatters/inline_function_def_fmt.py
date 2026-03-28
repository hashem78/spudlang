from typing import Callable

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.inline_function_def import InlineFunctionDef
from spud_fmt.config import FmtConfig
from spud_fmt.formatter_protocol import FormatterDispatch


class InlineFunctionDefFormatter:
    def __init__(self, config: FmtConfig, fmt: Callable[[], FormatterDispatch]):
        self._config = config
        self._fmt = fmt

    def format(self, node: ASTNode, depth: int) -> str:
        assert isinstance(node, InlineFunctionDef)
        param_names = [p.name for p in node.params]
        separator = ", " if self._config.space_after_comma else ","
        arrow = " => " if self._config.spaces_around_fat_arrow else "=>"
        body = self._fmt().format_node(node.body, depth)
        return f"({separator.join(param_names)}){arrow}{body}"
