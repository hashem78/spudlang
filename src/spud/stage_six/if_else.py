from typing import Literal

from spud.core.position import Position
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.condition_branch import ConditionBranch
from spud.stage_six.node_type import NodeType


class IfElse(ASTNode, frozen=True):
    node_type: Literal[NodeType.IF_ELSE] = NodeType.IF_ELSE
    position: Position
    branches: list[ConditionBranch]
    else_body: list[ASTNode] | None = None
