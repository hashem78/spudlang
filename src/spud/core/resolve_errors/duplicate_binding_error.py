from typing import Literal

from spud.core.resolve_errors.resolve_error import ResolveError
from spud.core.resolve_errors.resolve_error_kind import ResolveErrorKind


class DuplicateBindingError(ResolveError, frozen=True):
    kind: Literal[ResolveErrorKind.DUPLICATE_BINDING] = ResolveErrorKind.DUPLICATE_BINDING
    name: str
