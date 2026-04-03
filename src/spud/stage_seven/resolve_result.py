from pydantic import BaseModel

from spud.core.environment import Environment
from spud.stage_seven.resolve_error import ResolveError


class ResolveResult(BaseModel, frozen=True):
    errors: list[ResolveError]
    environment: Environment
