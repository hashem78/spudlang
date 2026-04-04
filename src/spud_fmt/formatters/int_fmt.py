from spud.stage_six import ASTNode, IntLiteral


class IntFormatter:
    def format(self, node: ASTNode, depth: int) -> str:
        match node:
            case IntLiteral(value=value):
                return str(value)
