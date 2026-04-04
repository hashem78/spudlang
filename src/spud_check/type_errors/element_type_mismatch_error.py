from typing import Literal

from spud.core.types import SpudTypeKind
from spud_check.type_errors.type_error import TypeError
from spud_check.type_errors.type_error_kind import TypeErrorKind


class ElementTypeMismatchError(TypeError, frozen=True):
    kind: Literal[TypeErrorKind.ELEMENT_TYPE_MISMATCH] = TypeErrorKind.ELEMENT_TYPE_MISMATCH
    name: str
    expected: SpudTypeKind
    actual: SpudTypeKind
