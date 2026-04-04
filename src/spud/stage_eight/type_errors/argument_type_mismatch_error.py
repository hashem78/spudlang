from typing import Literal

from spud.core.types.spud_type_kind import SpudTypeKind
from spud.stage_eight.type_errors.type_error import TypeError
from spud.stage_eight.type_errors.type_error_kind import TypeErrorKind


class ArgumentTypeMismatchError(TypeError, frozen=True):
    kind: Literal[TypeErrorKind.ARGUMENT_TYPE_MISMATCH] = TypeErrorKind.ARGUMENT_TYPE_MISMATCH
    name: str
    index: int
    expected: SpudTypeKind
    actual: SpudTypeKind
