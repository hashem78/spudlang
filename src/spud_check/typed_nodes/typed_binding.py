from spud.stage_six import TypeExpression
from spud_check.typed_nodes.typed_node import TypedNode


class TypedBinding(TypedNode, frozen=True):
    target_name: str
    type_annotation: TypeExpression
    value: TypedNode
