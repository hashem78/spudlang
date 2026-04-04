from pydantic import BaseModel

from spud.core.position import Position
from spud.stage_five.stage_five_token_type import StageFiveTokenType


class StageFiveToken(BaseModel, frozen=True):
    token_type: StageFiveTokenType
    position: Position
    value: str
