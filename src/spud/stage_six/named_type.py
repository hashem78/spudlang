from typing import Literal

from spud.stage_six.node_type import NodeType
from spud.stage_six.type_expression import TypeExpression


class NamedType(TypeExpression, frozen=True):
    node_type: Literal[NodeType.NAMED_TYPE] = NodeType.NAMED_TYPE
    name: str
