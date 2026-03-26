from typing import Generator

from structlog import BoundLogger

from spud.stage_three.stage_three_token import StageThreeToken
from spud.stage_three.stage_three_token_type import StageThreeTokenType
from spud.stage_two.stage_two import StageTwo
from spud.stage_two.stage_two_token import DefinedStageTwoToken, StageTwoToken
from spud.stage_two.stage_two_token_type import StageTwoTokenType


class StageThree:
    _SYMBOL_TYPES = {
        StageTwoTokenType.DOT,
        StageTwoTokenType.HYPHEN,
        StageTwoTokenType.COMMA,
        StageTwoTokenType.SEMICOLON,
        StageTwoTokenType.COLON,
        StageTwoTokenType.OCTOTHORPE,
        StageTwoTokenType.PERCENT,
        StageTwoTokenType.PLUS,
        StageTwoTokenType.ASTERISK,
        StageTwoTokenType.FORWARD_SLASH,
        StageTwoTokenType.BACKWARD_SLASH,
        StageTwoTokenType.ANGLED_LEFT,
        StageTwoTokenType.ANGLED_RIGHT,
        StageTwoTokenType.BRACKET_LEFT,
        StageTwoTokenType.BRACKET_RIGHT,
        StageTwoTokenType.PAREN_LEFT,
        StageTwoTokenType.PAREN_RIGHT,
        StageTwoTokenType.BRACE_LEFT,
        StageTwoTokenType.BRACE_RIGHT,
        StageTwoTokenType.EQUALS,
        StageTwoTokenType.EXCLAMATION,
        StageTwoTokenType.AMPERSAND,
        StageTwoTokenType.PIPE,
    }

    def __init__(self, stage_two: StageTwo, logger: BoundLogger):
        self._stage_two = stage_two
        self._logger = logger

    def parse(self) -> Generator[StageThreeToken, None, None]:
        buff: list[StageTwoToken] = []

        for token in self._stage_two.parse():
            match token.token_type:
                case StageTwoTokenType.SPACE:
                    if buff:
                        yield StageThreeToken(
                            token_type=StageThreeTokenType.IDENTIFIER,
                            position=buff[0].position,
                            value="".join(t.token_type.value for t in buff),
                        )
                        buff.clear()
                case StageTwoTokenType.NEW_LINE:
                    if buff:
                        yield StageThreeToken(
                            token_type=StageThreeTokenType.IDENTIFIER,
                            position=buff[0].position,
                            value="".join(t.token_type.value for t in buff),
                        )
                        buff.clear()
                    yield StageThreeToken(
                        token_type=StageThreeTokenType.NEW_LINE,
                        position=token.position,
                        value="\n",
                    )
                case token_type if token_type in self._SYMBOL_TYPES:
                    if buff:
                        yield StageThreeToken(
                            token_type=StageThreeTokenType.IDENTIFIER,
                            position=buff[0].position,
                            value="".join(t.token_type.value for t in buff),
                        )
                        buff.clear()
                    yield StageThreeToken(
                        token_type=StageThreeTokenType[token_type.name],
                        position=token.position,
                        value=token_type.value,
                    )
                case token_type if len(token_type.value) > 1:
                    if buff:
                        yield StageThreeToken(
                            token_type=StageThreeTokenType.IDENTIFIER,
                            position=buff[0].position,
                            value="".join(t.token_type.value for t in buff),
                        )
                        buff.clear()
                    yield StageThreeToken(
                        token_type=StageThreeTokenType[token_type.name],
                        position=token.position,
                        value=token.token_type.value
                        if isinstance(token, DefinedStageTwoToken)
                        else "".join([tk.token_type.value for tk in token.value]),
                    )
                case _:
                    buff.append(token)

        if buff:
            yield StageThreeToken(
                token_type=StageThreeTokenType.IDENTIFIER,
                position=buff[0].position,
                value="".join(t.token_type.value for t in buff),
            )
