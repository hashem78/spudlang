from spud.stage_six import ASTNode, StringLiteral
from spud_fmt.config import FmtConfig, QuoteStyle


class StringFormatter:
    def __init__(self, config: FmtConfig):
        self._config = config

    def format(self, node: ASTNode, depth: int) -> str:
        match node:
            case StringLiteral(value=value):
                match self._config.quote_style:
                    case QuoteStyle.SINGLE:
                        escaped = value.replace("\\", "\\\\").replace("'", "\\'")
                        return f"'{escaped}'"
                    case QuoteStyle.DOUBLE:
                        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
                        return f'"{escaped}"'
