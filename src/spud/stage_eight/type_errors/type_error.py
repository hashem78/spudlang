from pydantic import BaseModel

from spud.core.position import Position
from spud.stage_eight.type_errors.type_error_kind import TypeErrorKind


class TypeError(BaseModel, frozen=True):
    kind: TypeErrorKind
    position: Position
