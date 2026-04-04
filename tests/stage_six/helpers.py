from spud.core import StringReader
from spud.core.pipeline import ParsedProgram, Pipeline
from spud.di import Container
from spud.stage_six import Program

_CONTAINER = Container()
PIPELINE: Pipeline = _CONTAINER.pipeline()


def parse(text: str) -> Program:
    return PIPELINE.get(ParsedProgram, StringReader(text)).program
