from spud.stage_six.ast_node import ASTNode
from spud.stage_six.identifier import Identifier


class IdentifierFormatter:
    def format(self, node: ASTNode, depth: int) -> str:
        assert isinstance(node, Identifier)
        return node.name
