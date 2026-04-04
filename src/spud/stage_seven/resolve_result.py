from pydantic import BaseModel

from spud.core import Environment
from spud.core.resolve_errors import ResolveError
from spud.stage_six import Program


class ResolveResult(BaseModel, frozen=True):
    """The output of stage 7 scope resolution.

    Contains the list of semantic errors found during resolution,
    the final environment representing the global scope, and an
    updated ``Program`` with resolve errors appended to its
    ``errors`` list.

    :param errors: Semantic errors discovered during the AST walk.
        Empty for a valid program.
    :param environment: The resolved global-scope environment.  Inner
        scopes (functions, loops, branches) are reachable via the
        parent links of their own ``Environment`` instances, but only
        the outermost scope is stored here.
    :param program: The input program with resolve errors appended
        to ``Program.errors``, forming a unified error list alongside
        any parse errors from stage 6.
    """

    errors: list[ResolveError]
    environment: Environment
    program: Program
