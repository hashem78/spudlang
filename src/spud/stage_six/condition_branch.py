from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType


class ConditionBranch(ASTNode, frozen=True):
    node_type: Literal[NodeType.CONDITION_BRANCH] = NodeType.CONDITION_BRANCH
    condition: ASTNode
    body: list[ASTNode]
