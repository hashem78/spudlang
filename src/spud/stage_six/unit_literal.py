from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType


class UnitLiteral(ASTNode, frozen=True):
    node_type: Literal[NodeType.UNIT_LITERAL] = NodeType.UNIT_LITERAL
