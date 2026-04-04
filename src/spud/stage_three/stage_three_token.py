from pydantic import BaseModel

from spud.core.position import Position
from spud.stage_three.stage_three_token_type import StageThreeTokenType


class StageThreeToken(BaseModel, frozen=True):
    token_type: StageThreeTokenType
    position: Position
    value: str
