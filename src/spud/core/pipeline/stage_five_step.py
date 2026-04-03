from structlog import BoundLogger

from spud.core.pipeline.pipeline_step import PipelineStep
from spud.core.pipeline.stage_four_step import StageFourStep
from spud.core.reader_protocol import IReader
from spud.stage_five.stage_five import StageFive


class StageFiveStep(PipelineStep):
    def __init__(self, prev: StageFourStep, logger: BoundLogger):
        self._prev = prev
        self._logger = logger

    def __call__(self, source: IReader) -> StageFive:
        s4 = self._prev(source)
        return StageFive(s4, self._logger)
