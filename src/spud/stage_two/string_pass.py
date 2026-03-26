from typing import Generator

from spud.stage_one.stage_one import StageOne
from spud.stage_one.stage_one_token import StageOneToken
from spud.stage_one.stage_one_token_type import StageOneTokenType
from spud.stage_two.stage_two_token import StringLiteralStageTwoToken
from spud.stage_two.stage_two_token_type import StageTwoTokenType

StringPassToken = StageOneToken | StringLiteralStageTwoToken


class StringPass:
    _STR_CTX_INDICATORS = {StageOneTokenType.SINGLE_QUOTES, StageOneTokenType.DOUBLE_QUOTES}

    def __init__(self, stage_one: StageOne):
        self._stage_one = stage_one

    def parse(self) -> Generator[StringPassToken, None, None]:
        prev_was_backslash = False
        tokens = self._stage_one.parse()

        for token in tokens:
            if token.token_type in self._STR_CTX_INDICATORS and not prev_was_backslash:
                str_ctx_buff = [token]
                escaped = False
                while (inner_token := next(tokens, None)) is not None:
                    str_ctx_buff.append(inner_token)
                    if inner_token.token_type == StageOneTokenType.BACKWARD_SLASH:
                        escaped = not escaped
                    elif inner_token.token_type in self._STR_CTX_INDICATORS and not escaped:
                        break
                    else:
                        escaped = False

                yield StringLiteralStageTwoToken(
                    token_type=StageTwoTokenType.STRING,
                    position=str_ctx_buff[0].position,
                    value=str_ctx_buff,
                )
                prev_was_backslash = False
                continue

            yield token
            prev_was_backslash = token.token_type == StageOneTokenType.BACKWARD_SLASH
