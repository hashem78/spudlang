from spud.stage_six.ast_node import ASTNode
from spud.stage_six.int_literal import IntLiteral


class IntFormatter:
    def format(self, node: ASTNode, depth: int) -> str:
        match node:
            case IntLiteral(value=value):
                return str(value)
