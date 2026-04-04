from collections.abc import Callable

from spud.core.pipeline import TypeCheckedProgram

ParseFn = Callable[[str], TypeCheckedProgram]
