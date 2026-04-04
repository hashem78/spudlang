from spud.core.types.spud_type import SpudType
from spud_check.typed_nodes.typed_node import TypedNode


class TypedForLoop(TypedNode, frozen=True):
    variable_name: str
    variable_type: SpudType
    iterable: TypedNode
    body: list[TypedNode]
