from spud.core.types.spud_type import SpudType
from spud_check.typed_nodes.typed_function_def import TypedParam
from spud_check.typed_nodes.typed_node import TypedNode


class TypedInlineFunctionDef(TypedNode, frozen=True):
    params: list[TypedParam]
    return_type: SpudType
    body: TypedNode
