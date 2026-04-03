from spud.core.pipeline.parsed_program import ParsedProgram
from spud.core.pipeline.pipeline_step import PipelineStep
from spud.core.pipeline.stage_five_step import StageFiveStep
from spud.core.reader_protocol import IReader
from spud.stage_six.parsers.program_parser import ProgramParser
from spud.stage_six.token_stream import TokenStream


class ParseStep(PipelineStep):
    def __init__(self, prev: StageFiveStep, parser: ProgramParser):
        self._prev = prev
        self._parser = parser

    def __call__(self, source: IReader) -> ParsedProgram:
        s5 = self._prev(source)
        tokens = list(s5.parse())
        stream = TokenStream(tokens)
        program = self._parser.parse(stream)
        return ParsedProgram(tokens=tokens, program=program)
