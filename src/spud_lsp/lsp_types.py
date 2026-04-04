from collections.abc import Callable

from spud.core.pipeline import ResolvedProgram

ParseFn = Callable[[str], ResolvedProgram]
