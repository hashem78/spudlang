from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.identifier import Identifier
from spud.stage_six.node_type import NodeType


class InlineFunctionDef(ASTNode, frozen=True):
    node_type: Literal[NodeType.INLINE_FUNCTION_DEF] = NodeType.INLINE_FUNCTION_DEF
    params: list[Identifier]
    body: ASTNode
