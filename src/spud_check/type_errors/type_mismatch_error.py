from typing import Literal

from spud.core.types import SpudTypeKind
from spud_check.type_errors.type_error import TypeError
from spud_check.type_errors.type_error_kind import TypeErrorKind


class TypeMismatchError(TypeError, frozen=True):
    kind: Literal[TypeErrorKind.TYPE_MISMATCH] = TypeErrorKind.TYPE_MISMATCH
    name: str
    expected: SpudTypeKind
    actual: SpudTypeKind
