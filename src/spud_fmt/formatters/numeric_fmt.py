from spud.stage_six.ast_node import ASTNode
from spud.stage_six.numeric_literal import NumericLiteral


class NumericFormatter:
    def format(self, node: ASTNode, depth: int) -> str:
        assert isinstance(node, NumericLiteral)
        return str(node.value)
