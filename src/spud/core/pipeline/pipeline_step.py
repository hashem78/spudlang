from spud.core.pipeline.pipeline_stage import PipelineStage
from spud.core.reader_protocol import IReader


class PipelineStep:
    """Base class for pipeline steps.

    Each step is a callable that takes an ``IReader`` and returns
    a ``PipelineStage``.  Concrete steps override ``__call__`` with
    a more specific return type.
    """

    def __call__(self, source: IReader) -> PipelineStage:
        raise NotImplementedError
