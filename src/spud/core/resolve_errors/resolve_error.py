from pydantic import BaseModel

from spud.core.position import Position
from spud.core.resolve_errors.resolve_error_kind import ResolveErrorKind


class ResolveError(BaseModel, frozen=True):
    """A single semantic error produced by scope resolution."""

    kind: ResolveErrorKind
    position: Position
