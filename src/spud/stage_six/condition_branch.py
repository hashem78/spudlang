from typing import Literal

from spud.core.position import Position
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType


class ConditionBranch(ASTNode, frozen=True):
    node_type: Literal[NodeType.CONDITION_BRANCH] = NodeType.CONDITION_BRANCH
    position: Position
    condition: ASTNode
    body: list[ASTNode]
