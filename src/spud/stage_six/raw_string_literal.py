from typing import Literal

from spud.core.position import Position
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType


class RawStringLiteral(ASTNode, frozen=True):
    node_type: Literal[NodeType.RAW_STRING_LITERAL] = NodeType.RAW_STRING_LITERAL
    position: Position
    value: str
