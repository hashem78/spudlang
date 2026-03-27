from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType


class Program(ASTNode, frozen=True):
    node_type: Literal[NodeType.PROGRAM] = NodeType.PROGRAM
    body: list[ASTNode]
