from spud.core.pipeline.pipeline_step import PipelineStep
from spud.core.pipeline.resolve_step import ResolveStep
from spud.core.pipeline.type_checked_program import TypeCheckedProgram
from spud.core.reader_protocol import IReader
from spud.stage_eight.stage_eight import StageEight


class TypeCheckStep(PipelineStep):
    def __init__(self, prev: ResolveStep, checker: StageEight):
        self._prev = prev
        self._checker = checker

    def __call__(self, source: IReader) -> TypeCheckedProgram:
        resolved = self._prev(source)
        result = self._checker.check(resolved.program)
        return TypeCheckedProgram(
            tokens=resolved.tokens,
            program=resolved.program,
            resolve_result=resolved.resolve_result,
            type_check_result=result,
        )
