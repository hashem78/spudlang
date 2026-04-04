from typing import TypeVar, cast

from spud.core.pipeline.pipeline_stage import PipelineStage
from spud.core.pipeline.pipeline_step import PipelineStep
from spud.core.pipeline.type_checked_program import TypeCheckedProgram
from spud.core.reader_protocol import IReader

T = TypeVar("T", bound=PipelineStage)


class Pipeline:
    """Typed registry of pipeline steps keyed by the stage type they produce.

    Each step is a reusable factory (singleton) that produces a fresh
    stage chain when called with a reader.  The pipeline provides typed
    access via ``get(stage_type, source)``, where the return type is
    inferred from ``stage_type``.

    Example::

        pipeline = container.pipeline()
        result = pipeline.run(FileReader(path))
        s3 = pipeline.get(StageThree, FileReader(path))
    """

    def __init__(self, steps: dict[type[PipelineStage], PipelineStep]):
        self._steps = steps

    def get(self, stage_type: type[T], source: IReader) -> T:
        """Build the chain up to *stage_type* and return its output.

        :param stage_type: The stage or result type to produce.
        :param source: The input reader for this parse.
        :returns: An instance of *stage_type*.
        """
        step = self._steps[stage_type]
        return cast(T, step(source))

    def run(self, source: IReader) -> TypeCheckedProgram:
        """Run the full pipeline and return the type-checked program."""
        return self.get(TypeCheckedProgram, source)
