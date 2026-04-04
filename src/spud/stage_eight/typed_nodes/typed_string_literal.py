from spud.stage_eight.typed_nodes.typed_node import TypedNode


class TypedStringLiteral(TypedNode, frozen=True):
    value: str
