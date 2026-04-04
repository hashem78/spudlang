from pydantic import BaseModel

from spud_check.type_errors.type_error import TypeError
from spud_check.typed_nodes.typed_node import TypedNode


class TypeCheckResult(BaseModel, frozen=True):
    errors: list[TypeError]
    typed_program: TypedNode
