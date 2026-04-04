from typing import Literal

from spud.core.types.spud_type_kind import SpudTypeKind
from spud_check.type_errors.type_error import TypeError
from spud_check.type_errors.type_error_kind import TypeErrorKind


class OperatorTypeError(TypeError, frozen=True):
    kind: Literal[TypeErrorKind.OPERATOR_TYPE_ERROR] = TypeErrorKind.OPERATOR_TYPE_ERROR
    operator: str
    left: SpudTypeKind
    right: SpudTypeKind
