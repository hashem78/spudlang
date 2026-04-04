from spud.stage_eight.typed_nodes.typed_node import TypedNode
from spud.stage_six.type_expression import TypeExpression


class TypedBinding(TypedNode, frozen=True):
    target_name: str
    type_annotation: TypeExpression
    value: TypedNode
