from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.identifier import Identifier
from spud.stage_six.node_type import NodeType


class ForLoop(ASTNode, frozen=True):
    node_type: Literal[NodeType.FOR_LOOP] = NodeType.FOR_LOOP
    variable: Identifier
    iterable: ASTNode
    body: list[ASTNode]
