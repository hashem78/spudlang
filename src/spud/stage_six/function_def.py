from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType
from spud.stage_six.type_expression import TypeExpression
from spud.stage_six.typed_param import TypedParam


class FunctionDef(ASTNode, frozen=True):
    node_type: Literal[NodeType.FUNCTION_DEF] = NodeType.FUNCTION_DEF
    params: list[TypedParam]
    return_type: TypeExpression
    body: list[ASTNode]
