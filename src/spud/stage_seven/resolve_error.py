from enum import Enum

from pydantic import BaseModel

from spud.core.position import Position


class ResolveErrorKind(str, Enum):
    UNDEFINED_VARIABLE = "undefined_variable"
    DUPLICATE_BINDING = "duplicate_binding"
    SHADOWED_BINDING = "shadowed_binding"


class ResolveError(BaseModel, frozen=True):
    kind: ResolveErrorKind
    position: Position
    name: str
