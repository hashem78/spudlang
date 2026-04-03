from pydantic import BaseModel

from spud.core.pipeline.pipeline_stage import PipelineStage
from spud.stage_five.stage_five_token import StageFiveToken
from spud.stage_six.program import Program


class ParsedProgram(BaseModel, PipelineStage, frozen=True):
    """Output of the parse step (stages 1-6).

    Carries the stage 5 token list alongside the parsed AST so
    downstream consumers (e.g. semantic tokens) can access both.
    """

    tokens: list[StageFiveToken]
    program: Program
