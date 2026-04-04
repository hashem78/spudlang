from spud.stage_eight.typed_nodes.typed_node import TypedNode


class TypedFloatLiteral(TypedNode, frozen=True):
    value: float
