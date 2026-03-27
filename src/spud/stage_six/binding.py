from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.identifier import Identifier
from spud.stage_six.node_type import NodeType


class Binding(ASTNode, frozen=True):
    node_type: Literal[NodeType.BINDING] = NodeType.BINDING
    target: Identifier
    value: ASTNode
