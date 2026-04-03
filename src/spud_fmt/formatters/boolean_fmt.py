from spud.stage_six.ast_node import ASTNode
from spud.stage_six.boolean_literal import BooleanLiteral


class BooleanFormatter:
    def format(self, node: ASTNode, depth: int) -> str:
        match node:
            case BooleanLiteral(value=value):
                return "true" if value else "false"
