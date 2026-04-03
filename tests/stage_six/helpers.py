from spud.core.pipeline import ParsedProgram, Pipeline
from spud.core.string_reader import StringReader
from spud.di.container import Container
from spud.stage_six.program import Program

_CONTAINER = Container()
PIPELINE: Pipeline = _CONTAINER.pipeline()


def parse(text: str) -> Program:
    return PIPELINE.get(ParsedProgram, StringReader(text)).program
