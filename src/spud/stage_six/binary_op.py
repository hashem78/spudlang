from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType


class BinaryOp(ASTNode, frozen=True):
    node_type: Literal[NodeType.BINARY_OP] = NodeType.BINARY_OP
    left: ASTNode
    operator: str
    right: ASTNode
