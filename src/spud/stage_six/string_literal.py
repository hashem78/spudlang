from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType


class StringLiteral(ASTNode, frozen=True):
    node_type: Literal[NodeType.STRING_LITERAL] = NodeType.STRING_LITERAL
    value: str
