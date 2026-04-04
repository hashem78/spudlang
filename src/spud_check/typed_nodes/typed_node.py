from pydantic import BaseModel

from spud.core.position import Position
from spud.core.types.spud_type import SpudType


class TypedNode(BaseModel, frozen=True):
    resolved_type: SpudType
    position: Position
    end: Position
