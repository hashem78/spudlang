from spud.stage_six import ASTNode, UnitLiteral


class UnitLiteralFormatter:
    def format(self, node: ASTNode, depth: int) -> str:
        match node:
            case UnitLiteral():
                return "()"
