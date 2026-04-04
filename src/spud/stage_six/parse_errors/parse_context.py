from pydantic import BaseModel

from spud.stage_five.stage_five_token_type import StageFiveTokenType
from spud.stage_six.parse_errors.parse_context_kind import ParseContextKind


class ParseContext(BaseModel, frozen=True):
    kind: ParseContextKind
    delimiter: StageFiveTokenType | None = None


def ctx(kind: ParseContextKind) -> ParseContext:
    """Shorthand for creating a ParseContext."""
    return ParseContext(kind=kind)
