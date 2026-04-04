from spud.stage_eight.typed_nodes.typed_node import TypedNode


class TypedProgram(TypedNode, frozen=True):
    body: list[TypedNode]
