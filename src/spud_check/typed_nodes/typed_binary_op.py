from spud_check.typed_nodes.typed_node import TypedNode


class TypedBinaryOp(TypedNode, frozen=True):
    left: TypedNode
    operator: str
    right: TypedNode
