from typing import Literal

from spud.core.position import Position
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType


class BinaryOp(ASTNode, frozen=True):
    node_type: Literal[NodeType.BINARY_OP] = NodeType.BINARY_OP
    position: Position
    left: ASTNode
    operator: str
    right: ASTNode
