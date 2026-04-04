from spud_check.typed_nodes.typed_node import TypedNode


class TypedFunctionCall(TypedNode, frozen=True):
    callee_name: str
    args: list[TypedNode]
