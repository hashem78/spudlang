from enum import Enum

from pydantic import BaseModel

from spud.core.position import Position
from spud.stage_five.stage_five_token_type import StageFiveTokenType


class ParseErrorKind(str, Enum):
    UNEXPECTED_END = "unexpected_end"
    UNEXPECTED_TOKEN = "unexpected_token"


class ParseError(BaseModel, frozen=True):
    kind: ParseErrorKind
    position: Position
    expected: StageFiveTokenType | None = None
    got: StageFiveTokenType | None = None
