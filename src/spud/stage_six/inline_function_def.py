from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType
from spud.stage_six.type_expression import TypeExpression
from spud.stage_six.typed_param import TypedParam


class InlineFunctionDef(ASTNode, frozen=True):
    node_type: Literal[NodeType.INLINE_FUNCTION_DEF] = NodeType.INLINE_FUNCTION_DEF
    params: list[TypedParam]
    return_type: TypeExpression
    body: ASTNode
