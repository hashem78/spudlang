from typing import Literal

from spud.core.types.spud_type import SpudType
from spud.core.types.spud_type_kind import SpudTypeKind


class BoolType(SpudType, frozen=True):
    kind: Literal[SpudTypeKind.BOOL] = SpudTypeKind.BOOL
