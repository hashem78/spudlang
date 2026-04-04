from pydantic import BaseModel

from spud.stage_eight.type_errors.type_error import TypeError
from spud.stage_eight.typed_nodes.typed_node import TypedNode


class TypeCheckResult(BaseModel, frozen=True):
    errors: list[TypeError]
    typed_program: TypedNode
