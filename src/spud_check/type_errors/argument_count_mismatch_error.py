from typing import Literal

from spud_check.type_errors.type_error import TypeError
from spud_check.type_errors.type_error_kind import TypeErrorKind


class ArgumentCountMismatchError(TypeError, frozen=True):
    kind: Literal[TypeErrorKind.ARGUMENT_COUNT_MISMATCH] = TypeErrorKind.ARGUMENT_COUNT_MISMATCH
    name: str
    expected_count: int
    actual_count: int
