from spud.stage_six.ast_node import ASTNode
from spud.stage_six.string_literal import StringLiteral
from spud_fmt.config import FmtConfig, QuoteStyle


class StringFormatter:
    def __init__(self, config: FmtConfig):
        self._config = config

    def format(self, node: ASTNode, depth: int) -> str:
        assert isinstance(node, StringLiteral)
        match self._config.quote_style:
            case QuoteStyle.SINGLE:
                escaped = node.value.replace("\\", "\\\\").replace("'", "\\'")
                return f"'{escaped}'"
            case QuoteStyle.DOUBLE:
                escaped = node.value.replace("\\", "\\\\").replace('"', '\\"')
                return f'"{escaped}"'
