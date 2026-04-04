from pydantic import BaseModel

from spud.core import Position
from spud_check.type_errors.type_error_kind import TypeErrorKind


class TypeError(BaseModel, frozen=True):
    kind: TypeErrorKind
    position: Position
