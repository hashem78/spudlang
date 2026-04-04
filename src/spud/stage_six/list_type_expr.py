from typing import Literal

from spud.stage_six.node_type import NodeType
from spud.stage_six.type_expression import TypeExpression


class ListTypeExpr(TypeExpression, frozen=True):
    node_type: Literal[NodeType.LIST_TYPE] = NodeType.LIST_TYPE
    element: TypeExpression
