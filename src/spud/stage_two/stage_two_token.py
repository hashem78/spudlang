from typing import Literal

from pydantic import BaseModel

from spud.core.position import Position
from spud.stage_one.stage_one_token import StageOneToken
from spud.stage_two.stage_two_token_type import StageTwoTokenType


class DefinedStageTwoToken(BaseModel):
    token_type: StageTwoTokenType
    position: Position


class StringLiteralStageTwoToken(BaseModel):
    token_type: Literal[StageTwoTokenType.STRING] = StageTwoTokenType.STRING
    position: Position
    value: list[StageOneToken]


class RawStringLiteralStageTwoToken(BaseModel):
    token_type: Literal[StageTwoTokenType.RAW_STRING] = StageTwoTokenType.RAW_STRING
    position: Position
    value: list[StageOneToken]


StringStageTwoToken = StringLiteralStageTwoToken | RawStringLiteralStageTwoToken
StageTwoToken = DefinedStageTwoToken | StringStageTwoToken
