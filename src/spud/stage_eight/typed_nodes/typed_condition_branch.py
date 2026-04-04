from spud.stage_eight.typed_nodes.typed_node import TypedNode


class TypedConditionBranch(TypedNode, frozen=True):
    condition: TypedNode
    body: list[TypedNode]
