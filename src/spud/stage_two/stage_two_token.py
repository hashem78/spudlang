from pydantic import BaseModel

from spud.core.position import Position
from spud.stage_two.stage_two_token_type import StageTwoTokenType


class StageTwoToken(BaseModel):
    token_type: StageTwoTokenType
    position: Position
