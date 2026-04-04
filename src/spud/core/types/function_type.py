from typing import Literal

from spud.core.types.spud_type import SpudType
from spud.core.types.spud_type_kind import SpudTypeKind


class FunctionType(SpudType, frozen=True):
    kind: Literal[SpudTypeKind.FUNCTION] = SpudTypeKind.FUNCTION
    params: tuple[SpudType, ...]
    returns: SpudType
