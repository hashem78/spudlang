from typing import Literal

from spud_check.type_errors.type_error import TypeError
from spud_check.type_errors.type_error_kind import TypeErrorKind


class NotCallableError(TypeError, frozen=True):
    kind: Literal[TypeErrorKind.NOT_CALLABLE] = TypeErrorKind.NOT_CALLABLE
    name: str
