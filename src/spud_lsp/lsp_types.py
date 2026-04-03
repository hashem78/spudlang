from collections.abc import Callable

from pydantic import BaseModel

from spud.stage_five.stage_five_token import StageFiveToken
from spud.stage_seven.resolve_result import ResolveResult


class ParseResult(BaseModel, frozen=True):
    resolve_result: ResolveResult
    tokens: list[StageFiveToken]


ParseFn = Callable[[str], ParseResult]
