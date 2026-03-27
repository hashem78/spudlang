from enum import Enum

from pydantic import BaseModel

from spud.core.position import Position
from spud.stage_five.stage_five_token import StageFiveToken
from spud.stage_five.stage_five_token_type import StageFiveTokenType


class ParseErrorKind(str, Enum):
    UNEXPECTED_END = "unexpected_end"
    UNEXPECTED_TOKEN = "unexpected_token"


class ParseError(BaseModel, frozen=True):
    kind: ParseErrorKind
    position: Position
    expected: StageFiveTokenType | None = None
    got: StageFiveTokenType | None = None


class TokenStream:
    """Cursor over a flat list of stage five tokens with expect/consume primitives."""

    def __init__(self, tokens: list[StageFiveToken]):
        self._tokens = tokens
        self._pos = 0

    def at_end(self) -> bool:
        return self._pos >= len(self._tokens)

    def peek(self) -> StageFiveToken | None:
        if self.at_end():
            return None
        return self._tokens[self._pos]

    def consume(self) -> StageFiveToken | ParseError:
        """Advance past the current token and return it."""
        if self.at_end():
            position = self._tokens[-1].position if self._tokens else Position(line=0, column=0)
            return ParseError(kind=ParseErrorKind.UNEXPECTED_END, position=position)
        token = self._tokens[self._pos]
        self._pos += 1
        return token

    def expect(self, token_type: StageFiveTokenType) -> StageFiveToken | ParseError:
        """Consume the current token, asserting it matches the expected type."""
        result = self.consume()
        if isinstance(result, ParseError):
            return ParseError(
                kind=ParseErrorKind.UNEXPECTED_END,
                position=result.position,
                expected=token_type,
            )
        if result.token_type != token_type:
            return ParseError(
                kind=ParseErrorKind.UNEXPECTED_TOKEN,
                position=result.position,
                expected=token_type,
                got=result.token_type,
            )
        return result
