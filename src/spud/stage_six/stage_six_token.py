from __future__ import annotations

from pydantic import BaseModel

from spud.core.position import Position
from spud.stage_four.stage_four_token import StageFourToken
from spud.stage_six.stage_six_token_type import StageSixTokenType


class StageSixToken(BaseModel):
    token_type: StageSixTokenType
    position: Position
    tokens: list[StageFourToken]
    children: list[StageSixToken] = []
