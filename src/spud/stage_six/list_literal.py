from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType


class ListLiteral(ASTNode, frozen=True):
    node_type: Literal[NodeType.LIST_LITERAL] = NodeType.LIST_LITERAL
    elements: list[ASTNode]
