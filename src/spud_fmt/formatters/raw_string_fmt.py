from spud.stage_six import ASTNode, RawStringLiteral


class RawStringFormatter:
    def format(self, node: ASTNode, depth: int) -> str:
        match node:
            case RawStringLiteral(value=value):
                return f"`{value}`"
