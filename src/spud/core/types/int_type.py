from typing import Literal

from spud.core.types.spud_type import SpudType
from spud.core.types.spud_type_kind import SpudTypeKind


class IntType(SpudType, frozen=True):
    kind: Literal[SpudTypeKind.INT] = SpudTypeKind.INT
