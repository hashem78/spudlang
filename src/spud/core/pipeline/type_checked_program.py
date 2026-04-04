from pydantic import BaseModel

from spud.core.pipeline.pipeline_stage import PipelineStage
from spud.stage_eight.type_check_result import TypeCheckResult
from spud.stage_five.stage_five_token import StageFiveToken
from spud.stage_seven.resolve_result import ResolveResult
from spud.stage_six.program import Program


class TypeCheckedProgram(BaseModel, PipelineStage, frozen=True):
    """Output of the full pipeline (stages 1-8).

    Carries tokens, the program with all errors, the resolve result
    with the environment tree, and the type check result with the
    typed AST.
    """

    tokens: list[StageFiveToken]
    program: Program
    resolve_result: ResolveResult
    type_check_result: TypeCheckResult
