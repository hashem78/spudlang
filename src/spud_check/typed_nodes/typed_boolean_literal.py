from spud_check.typed_nodes.typed_node import TypedNode


class TypedBooleanLiteral(TypedNode, frozen=True):
    value: bool
