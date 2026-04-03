from pydantic import BaseModel

from spud.core.environment import Environment
from spud.stage_seven.resolve_error import ResolveError


class ResolveResult(BaseModel, frozen=True):
    """The output of stage 7 scope resolution.

    Contains both the list of semantic errors found during resolution
    and the final environment representing the global scope after all
    top-level bindings have been processed.

    :param errors: Semantic errors discovered during the AST walk.
        Empty for a valid program.
    :param environment: The resolved global-scope environment.  Inner
        scopes (functions, loops, branches) are reachable via the
        parent links of their own ``Environment`` instances, but only
        the outermost scope is stored here.

    Example — a valid program::

        >>> result.errors
        []
        >>> result.environment.bindings.keys()
        dict_keys(['x', 'f'])

    Example — a program with an undefined variable::

        >>> result.errors[0].kind
        <ResolveErrorKind.UNDEFINED_VARIABLE: 'undefined_variable'>
    """

    errors: list[ResolveError]
    environment: Environment
