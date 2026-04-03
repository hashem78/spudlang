from spud.core.pipeline.parse_step import ParseStep
from spud.core.pipeline.pipeline_step import PipelineStep
from spud.core.pipeline.resolved_program import ResolvedProgram
from spud.core.reader_protocol import IReader
from spud.stage_seven.stage_seven import StageSeven


class ResolveStep(PipelineStep):
    def __init__(self, prev: ParseStep, resolver: StageSeven):
        self._prev = prev
        self._resolver = resolver

    def __call__(self, source: IReader) -> ResolvedProgram:
        parsed = self._prev(source)
        result = self._resolver.resolve(parsed.program)
        return ResolvedProgram(
            tokens=parsed.tokens,
            program=result.program,
            resolve_result=result,
        )
