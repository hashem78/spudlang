from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType


class IntLiteral(ASTNode, frozen=True):
    node_type: Literal[NodeType.INT_LITERAL] = NodeType.INT_LITERAL
    value: int
