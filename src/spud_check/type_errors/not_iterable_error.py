from typing import Literal

from spud.core.types import SpudTypeKind
from spud_check.type_errors.type_error import TypeError
from spud_check.type_errors.type_error_kind import TypeErrorKind


class NotIterableError(TypeError, frozen=True):
    kind: Literal[TypeErrorKind.NOT_ITERABLE] = TypeErrorKind.NOT_ITERABLE
    actual: SpudTypeKind
