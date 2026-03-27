from collections.abc import Callable

from spud.stage_six.parse_error import ParseError
from spud.stage_six.program import Program

ParseResult = Program | ParseError
ParseFn = Callable[[str], ParseResult]
