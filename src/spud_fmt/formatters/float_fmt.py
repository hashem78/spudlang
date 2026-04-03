from spud.stage_six.ast_node import ASTNode
from spud.stage_six.float_literal import FloatLiteral
from spud_fmt.config import FmtConfig


class FloatFormatter:
    def __init__(self, config: FmtConfig):
        self._config = config

    def format(self, node: ASTNode, depth: int) -> str:
        assert isinstance(node, FloatLiteral)
        text = str(node.value)
        if not self._config.normalize_leading_zero and text.startswith("0."):
            text = text[1:]
        if not self._config.normalize_trailing_zero and text.endswith(".0"):
            text = text[:-1]
        return text
