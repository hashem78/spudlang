from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType


class FloatLiteral(ASTNode, frozen=True):
    node_type: Literal[NodeType.FLOAT_LITERAL] = NodeType.FLOAT_LITERAL
    value: float
