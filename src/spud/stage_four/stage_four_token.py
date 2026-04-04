from pydantic import BaseModel

from spud.core.position import Position
from spud.stage_four.stage_four_token_type import StageFourTokenType


class StageFourToken(BaseModel, frozen=True):
    token_type: StageFourTokenType
    position: Position
    value: str
