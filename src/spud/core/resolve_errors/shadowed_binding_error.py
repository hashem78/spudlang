from typing import Literal

from spud.core.resolve_errors.resolve_error import ResolveError
from spud.core.resolve_errors.resolve_error_kind import ResolveErrorKind


class ShadowedBindingError(ResolveError, frozen=True):
    kind: Literal[ResolveErrorKind.SHADOWED_BINDING] = ResolveErrorKind.SHADOWED_BINDING
    name: str
