from typing import Literal

from spud.stage_six.node_type import NodeType
from spud.stage_six.type_expression import TypeExpression


class FunctionTypeExpr(TypeExpression, frozen=True):
    node_type: Literal[NodeType.FUNCTION_TYPE] = NodeType.FUNCTION_TYPE
    params: list[TypeExpression]
    returns: TypeExpression
