from spud.stage_six import ASTNode, Identifier


class IdentifierFormatter:
    def format(self, node: ASTNode, depth: int) -> str:
        match node:
            case Identifier(name=name):
                return name
