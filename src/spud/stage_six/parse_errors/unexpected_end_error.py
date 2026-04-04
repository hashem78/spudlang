from typing import Literal

from spud.stage_five.stage_five_token_type import StageFiveTokenType
from spud.stage_six.parse_errors.parse_error import ParseError
from spud.stage_six.parse_errors.parse_error_kind import ParseErrorKind


class UnexpectedEndError(ParseError, frozen=True):
    kind: Literal[ParseErrorKind.UNEXPECTED_END] = ParseErrorKind.UNEXPECTED_END
    expected: StageFiveTokenType | None = None
