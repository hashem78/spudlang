from typing import Literal

from spud.core.position import Position
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType


class NumericLiteral(ASTNode, frozen=True):
    node_type: Literal[NodeType.NUMERIC_LITERAL] = NodeType.NUMERIC_LITERAL
    position: Position
    value: int
