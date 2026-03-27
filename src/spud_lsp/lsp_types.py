from collections.abc import Callable

from spud.stage_six.program import Program

ParseFn = Callable[[str], Program]
