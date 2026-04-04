from pydantic import BaseModel

from spud.core.position import Position
from spud.stage_one.stage_one_token_type import StageOneTokenType


class StageOneToken(BaseModel, frozen=True):
    token_type: StageOneTokenType
    position: Position
