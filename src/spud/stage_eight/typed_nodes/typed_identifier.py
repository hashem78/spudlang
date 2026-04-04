from spud.stage_eight.typed_nodes.typed_node import TypedNode


class TypedIdentifier(TypedNode, frozen=True):
    name: str
