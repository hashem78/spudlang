from spud.stage_six import ASTNode, BooleanLiteral


class BooleanFormatter:
    def format(self, node: ASTNode, depth: int) -> str:
        match node:
            case BooleanLiteral(value=value):
                return "true" if value else "false"
