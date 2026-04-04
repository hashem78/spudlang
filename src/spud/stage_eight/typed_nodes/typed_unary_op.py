from spud.stage_eight.typed_nodes.typed_node import TypedNode


class TypedUnaryOp(TypedNode, frozen=True):
    operator: str
    operand: TypedNode
