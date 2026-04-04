from typing import Literal

from spud.core.types.spud_type import SpudType
from spud.core.types.spud_type_kind import SpudTypeKind


class ListType(SpudType, frozen=True):
    kind: Literal[SpudTypeKind.LIST] = SpudTypeKind.LIST
    element: SpudType
