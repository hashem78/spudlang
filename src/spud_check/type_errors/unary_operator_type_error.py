from typing import Literal

from spud.core.types.spud_type_kind import SpudTypeKind
from spud_check.type_errors.type_error import TypeError
from spud_check.type_errors.type_error_kind import TypeErrorKind


class UnaryOperatorTypeError(TypeError, frozen=True):
    kind: Literal[TypeErrorKind.UNARY_OPERATOR_TYPE_ERROR] = TypeErrorKind.UNARY_OPERATOR_TYPE_ERROR
    operator: str
    operand: SpudTypeKind
