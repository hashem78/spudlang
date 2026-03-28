from spud.stage_six.ast_node import ASTNode
from spud.stage_six.unit_literal import UnitLiteral


class UnitLiteralFormatter:
    def format(self, node: ASTNode, depth: int) -> str:
        assert isinstance(node, UnitLiteral)
        return "()"
