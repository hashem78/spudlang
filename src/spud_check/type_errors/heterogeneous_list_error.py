from typing import Literal

from spud.core.types import SpudTypeKind
from spud_check.type_errors.type_error import TypeError
from spud_check.type_errors.type_error_kind import TypeErrorKind


class HeterogeneousListError(TypeError, frozen=True):
    kind: Literal[TypeErrorKind.HETEROGENEOUS_LIST] = TypeErrorKind.HETEROGENEOUS_LIST
    index: int
    expected: SpudTypeKind
    actual: SpudTypeKind
