from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType


class Identifier(ASTNode, frozen=True):
    node_type: Literal[NodeType.IDENTIFIER] = NodeType.IDENTIFIER
    name: str
