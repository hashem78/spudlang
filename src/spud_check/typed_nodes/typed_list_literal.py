from spud_check.typed_nodes.typed_node import TypedNode


class TypedListLiteral(TypedNode, frozen=True):
    elements: list[TypedNode]
