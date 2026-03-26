from typing import Generator

from spud.stage_one.stage_one import StageOne
from spud.stage_one.stage_one_token import StageOneToken
from spud.stage_one.stage_one_token_type import StageOneTokenType
from spud.stage_two.stage_two_token import (
    RawStringLiteralStageTwoToken,
    StringLiteralStageTwoToken,
    StringStageTwoToken,
)
from spud.stage_two.stage_two_token_type import StageTwoTokenType

StringPassToken = StageOneToken | StringStageTwoToken


def _consume_until(
    opening: StageOneToken,
    closing_type: StageOneTokenType,
    tokens: Generator[StageOneToken, None, None],
    escape: bool,
) -> list[StageOneToken]:
    """Consume tokens until a closing delimiter is found.

    When ``escape`` is True, a backslash before the closing delimiter
    prevents it from closing the string. When False, content is raw.
    """
    buff = [opening]
    escaped = False
    while (inner := next(tokens, None)) is not None:
        buff.append(inner)
        if escape and inner.token_type == StageOneTokenType.BACKWARD_SLASH:
            escaped = not escaped
        elif inner.token_type == closing_type and not escaped:
            break
        else:
            escaped = False
    return buff


class StringPass:
    _STR_CTX_INDICATORS = {StageOneTokenType.SINGLE_QUOTES, StageOneTokenType.DOUBLE_QUOTES}

    def __init__(self, stage_one: StageOne):
        self._stage_one = stage_one

    def parse(self) -> Generator[StringPassToken, None, None]:
        prev_was_backslash = False
        tokens = self._stage_one.parse()

        for token in tokens:
            if token.token_type == StageOneTokenType.BACKTICK:
                buff = _consume_until(token, StageOneTokenType.BACKTICK, tokens, escape=False)
                yield RawStringLiteralStageTwoToken(
                    position=token.position,
                    value=buff,
                )
                prev_was_backslash = False
                continue

            if token.token_type in self._STR_CTX_INDICATORS and not prev_was_backslash:
                buff = _consume_until(token, token.token_type, tokens, escape=True)
                yield StringLiteralStageTwoToken(
                    token_type=StageTwoTokenType.STRING,
                    position=token.position,
                    value=buff,
                )
                prev_was_backslash = False
                continue

            yield token
            prev_was_backslash = token.token_type == StageOneTokenType.BACKWARD_SLASH
