from typing import Literal

from spud.core.types import SpudTypeKind
from spud_check.type_errors.type_error import TypeError
from spud_check.type_errors.type_error_kind import TypeErrorKind


class ArgumentTypeMismatchError(TypeError, frozen=True):
    kind: Literal[TypeErrorKind.ARGUMENT_TYPE_MISMATCH] = TypeErrorKind.ARGUMENT_TYPE_MISMATCH
    name: str
    index: int
    expected: SpudTypeKind
    actual: SpudTypeKind
