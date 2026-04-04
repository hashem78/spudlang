from typing import Literal

from spud.core.types.spud_type_kind import SpudTypeKind
from spud.stage_eight.type_errors.type_error import TypeError
from spud.stage_eight.type_errors.type_error_kind import TypeErrorKind


class ConditionNotBoolError(TypeError, frozen=True):
    kind: Literal[TypeErrorKind.CONDITION_NOT_BOOL] = TypeErrorKind.CONDITION_NOT_BOOL
    actual: SpudTypeKind
