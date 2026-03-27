from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType


class BooleanLiteral(ASTNode, frozen=True):
    node_type: Literal[NodeType.BOOLEAN_LITERAL] = NodeType.BOOLEAN_LITERAL
    value: bool
