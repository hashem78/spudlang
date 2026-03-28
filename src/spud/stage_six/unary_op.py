from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType


class UnaryOp(ASTNode, frozen=True):
    node_type: Literal[NodeType.UNARY_OP] = NodeType.UNARY_OP
    operator: str
    operand: ASTNode
