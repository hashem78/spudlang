from typing import Literal

from spud.stage_eight.type_errors.type_error import TypeError
from spud.stage_eight.type_errors.type_error_kind import TypeErrorKind


class UnknownTypeError(TypeError, frozen=True):
    kind: Literal[TypeErrorKind.UNKNOWN_TYPE] = TypeErrorKind.UNKNOWN_TYPE
    name: str
