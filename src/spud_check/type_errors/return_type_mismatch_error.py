from typing import Literal

from spud.core.types import SpudTypeKind
from spud_check.type_errors.type_error import TypeError
from spud_check.type_errors.type_error_kind import TypeErrorKind


class ReturnTypeMismatchError(TypeError, frozen=True):
    kind: Literal[TypeErrorKind.RETURN_TYPE_MISMATCH] = TypeErrorKind.RETURN_TYPE_MISMATCH
    expected: SpudTypeKind
    actual: SpudTypeKind
