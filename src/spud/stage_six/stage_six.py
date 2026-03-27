from structlog import BoundLogger

from spud.stage_five.stage_five import StageFive
from spud.stage_six.parsers.program_parser import ProgramParser
from spud.stage_six.program import Program
from spud.stage_six.token_stream import TokenStream


class StageSix:
    def __init__(self, stage_five: StageFive, program_parser: ProgramParser, logger: BoundLogger):
        self._stage_five = stage_five
        self._program_parser = program_parser
        self._logger = logger

    def parse(self) -> Program:
        """Parse stage five tokens into an AST."""
        tokens = list(self._stage_five.parse())
        stream = TokenStream(tokens)
        return self._program_parser.parse(stream)
