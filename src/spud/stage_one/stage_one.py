from typing import Generator

from spud.core.position import Position
from spud.core.reader_protocol import IReader
from spud.stage_one.stage_one_token import StageOneToken
from spud.stage_one.stage_one_token_type import StageOneTokenType


class StageOne:
    def __init__(self, handle: IReader):
        self._handle = handle

    def parse(self) -> Generator[StageOneToken, None, None]:
        line = 1
        column = 0

        for raw_token in self._handle.read():
            position = Position(line=line, column=column)
            yield StageOneToken(
                token_type=StageOneTokenType(raw_token),
                position=position,
            )

            if raw_token == "\n":
                line += 1
                column = 1
            else:
                column += 1
