from pydantic import BaseModel

from spud.core.position import Position
from spud.stage_one.stage_one_token_type import StageOneTokenType


class StageOneToken(BaseModel):
    token_type: StageOneTokenType
    position: Position
