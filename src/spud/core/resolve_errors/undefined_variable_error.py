from typing import Literal

from spud.core.resolve_errors.resolve_error import ResolveError
from spud.core.resolve_errors.resolve_error_kind import ResolveErrorKind


class UndefinedVariableError(ResolveError, frozen=True):
    kind: Literal[ResolveErrorKind.UNDEFINED_VARIABLE] = ResolveErrorKind.UNDEFINED_VARIABLE
    name: str
