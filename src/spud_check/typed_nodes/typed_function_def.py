from spud.core.types import SpudType
from spud_check.typed_nodes.typed_node import TypedNode


class TypedParam(TypedNode, frozen=True):
    name: str
    declared_type: SpudType


class TypedFunctionDef(TypedNode, frozen=True):
    params: list[TypedParam]
    return_type: SpudType
    body: list[TypedNode]
