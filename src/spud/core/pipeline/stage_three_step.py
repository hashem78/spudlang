from structlog import BoundLogger

from spud.core.pipeline.pipeline_step import PipelineStep
from spud.core.pipeline.stage_two_step import StageTwoStep
from spud.core.reader_protocol import IReader
from spud.stage_three.stage_three import StageThree


class StageThreeStep(PipelineStep):
    def __init__(self, prev: StageTwoStep, logger: BoundLogger):
        self._prev = prev
        self._logger = logger

    def __call__(self, source: IReader) -> StageThree:
        s2 = self._prev(source)
        return StageThree(s2, self._logger)
