from structlog import BoundLogger

from spud.stage_five.stage_five import StageFive
from spud.stage_six.parser import TokenStream
from spud.stage_six.program import Program


class StageSix:
    def __init__(self, stage_five: StageFive, logger: BoundLogger):
        self._stage_five = stage_five
        self._logger = logger

    def parse(self) -> Program:
        """Parse stage five tokens into an AST."""
        tokens = list(self._stage_five.parse())
        _stream = TokenStream(tokens)
        return Program(body=[])
