from spud.core.position import Position
from spud.stage_five.stage_five_token import StageFiveToken
from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_six.parse_error import ParseContext, ParseError, ParseErrorKind


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

    def peek_type(self) -> T | None:
        tok = self.peek()
        return tok.token_type if tok else None

    def peek_at(self, offset: int) -> StageFiveToken | None:
        idx = self._pos + offset
        if idx >= len(self._tokens):
            return None
        return self._tokens[idx]

    def consume(self, context: ParseContext | None = None) -> StageFiveToken | ParseError:
        """Advance past the current token and return it."""
        if self.at_end():
            position = self._tokens[-1].position if self._tokens else Position(line=0, column=0)
            return ParseError(kind=ParseErrorKind.UNEXPECTED_END, position=position, context=context)
        token = self._tokens[self._pos]
        self._pos += 1
        return token

    def expect(self, token_type: T, context: ParseContext | None = None) -> StageFiveToken | ParseError:
        """Consume the current token, asserting it matches the expected type."""
        result = self.consume(context=context)
        if isinstance(result, ParseError):
            return ParseError(
                kind=ParseErrorKind.UNEXPECTED_END,
                position=result.position,
                expected=token_type,
                context=context,
            )
        if result.token_type != token_type:
            return ParseError(
                kind=ParseErrorKind.UNEXPECTED_TOKEN,
                position=result.position,
                expected=token_type,
                got=result.token_type,
                context=context,
            )
        return result

    def skip_to_recovery(self) -> None:
        """Skip tokens until a statement boundary for error recovery.

        Consumes tokens until it finds a NEW_LINE (consumes it),
        then if an indented block follows (INDENT), skips the
        entire block (matching INDENT/DEDENT) before returning.
        Stops without consuming at DEDENT (end of enclosing
        block) or EOF.
        """
        while not self.at_end():
            match self.peek_type():
                case T.NEW_LINE:
                    self.consume()
                    self._skip_trailing_block()
                    return
                case T.DEDENT:
                    self.consume()
                    return
                case _:
                    self.consume()

    def _skip_trailing_block(self) -> None:
        """If the current token is INDENT, skip the entire block."""
        if self.peek_type() != T.INDENT:
            return
        depth: int = 0
        while not self.at_end():
            match self.peek_type():
                case T.INDENT:
                    depth += 1
                    self.consume()
                case T.DEDENT:
                    depth -= 1
                    self.consume()
                    if depth == 0:
                        return
                case _:
                    self.consume()
