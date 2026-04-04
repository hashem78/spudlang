from typing import Literal

from spud.core.types import SpudTypeKind
from spud_check.type_errors.type_error import TypeError
from spud_check.type_errors.type_error_kind import TypeErrorKind


class BranchTypeMismatchError(TypeError, frozen=True):
    kind: Literal[TypeErrorKind.BRANCH_TYPE_MISMATCH] = TypeErrorKind.BRANCH_TYPE_MISMATCH
    index: int
    expected: SpudTypeKind
    actual: SpudTypeKind
