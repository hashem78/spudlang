from spud.core.pipeline.pipeline_step import PipelineStep
from spud.core.reader_protocol import IReader
from spud.stage_one.stage_one import StageOne


class StageOneStep(PipelineStep):
    def __call__(self, source: IReader) -> StageOne:
        return StageOne(source)
