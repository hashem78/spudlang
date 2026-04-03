from spud.stage_six.ast_node import ASTNode
from spud.stage_six.identifier import Identifier


class IdentifierFormatter:
    def format(self, node: ASTNode, depth: int) -> str:
        match node:
            case Identifier(name=name):
                return name
