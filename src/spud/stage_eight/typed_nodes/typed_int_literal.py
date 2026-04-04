from spud.stage_eight.typed_nodes.typed_node import TypedNode


class TypedIntLiteral(TypedNode, frozen=True):
    value: int
