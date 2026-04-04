from spud.core.types.spud_type import SpudType
from spud.stage_eight.typed_nodes.typed_node import TypedNode


class TypedParam(TypedNode, frozen=True):
    name: str
    declared_type: SpudType


class TypedFunctionDef(TypedNode, frozen=True):
    params: list[TypedParam]
    return_type: SpudType
    body: list[TypedNode]
