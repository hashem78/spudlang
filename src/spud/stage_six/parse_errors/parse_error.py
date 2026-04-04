from pydantic import BaseModel

from spud.core.position import Position
from spud.stage_six.parse_errors.parse_context import ParseContext
from spud.stage_six.parse_errors.parse_error_kind import ParseErrorKind


class ParseError(BaseModel, frozen=True):
    kind: ParseErrorKind
    position: Position
    context: ParseContext | None = None


def with_context(error: ParseError, context: ParseContext) -> ParseError:
    """Attach context to an error if it doesn't already have one."""
    if error.context is None:
        return error.model_copy(update={"context": context})
    return error
