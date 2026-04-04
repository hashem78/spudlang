from pydantic import BaseModel

from spud.core.types.spud_type_kind import SpudTypeKind


class SpudType(BaseModel, frozen=True):
    kind: SpudTypeKind
