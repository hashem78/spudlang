from spud.core.types.spud_type import SpudType
from spud.stage_eight.typed_nodes.typed_function_def import TypedParam
from spud.stage_eight.typed_nodes.typed_node import TypedNode


class TypedInlineFunctionDef(TypedNode, frozen=True):
    params: list[TypedParam]
    return_type: SpudType
    body: TypedNode
