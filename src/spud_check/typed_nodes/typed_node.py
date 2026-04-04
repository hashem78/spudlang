from pydantic import BaseModel

from spud.core import Position
from spud.core.types import SpudType


class TypedNode(BaseModel, frozen=True):
    resolved_type: SpudType
    position: Position
    end: Position
