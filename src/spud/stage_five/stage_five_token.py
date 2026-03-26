from __future__ import annotations

from pydantic import BaseModel

from spud.core.position import Position
from spud.stage_five.stage_five_token_type import StageFiveTokenType
from spud.stage_four.stage_four_token import StageFourToken


class StageFiveToken(BaseModel):
    token_type: StageFiveTokenType
    position: Position
    tokens: list[StageFourToken]
    children: list[StageFiveToken] = []
