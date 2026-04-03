from enum import Enum

from pydantic import BaseModel

from spud.core.position import Position


class ResolveErrorKind(str, Enum):
    """Categories of semantic errors detected during scope resolution.

    .. attribute:: UNDEFINED_VARIABLE

        A name was referenced but never bound in any reachable scope.

        Example — ``y`` is not defined::

            result := y + 1

    .. attribute:: DUPLICATE_BINDING

        A name was bound more than once in the **same** scope.

        Example — ``x`` is bound twice at the top level::

            x := 1
            x := 2    # duplicate_binding

    .. attribute:: SHADOWED_BINDING

        A name in an inner scope collides with an identical name in an
        outer scope.  Spud forbids all shadowing — a name may only be
        bound once across the entire scope chain.

        Example — parameter ``x`` shadows the outer ``x``::

            x := 5
            f := (x) =>    # shadowed_binding
              x + 1
    """

    UNDEFINED_VARIABLE = "undefined_variable"
    DUPLICATE_BINDING = "duplicate_binding"
    SHADOWED_BINDING = "shadowed_binding"


class ResolveError(BaseModel, frozen=True):
    """A single semantic error produced by scope resolution.

    :param kind: The category of error (see :class:`ResolveErrorKind`).
    :param position: Source location where the error was detected.
    :param name: The binding or variable name involved.

    Example::

        >>> error = ResolveError(
        ...     kind=ResolveErrorKind.UNDEFINED_VARIABLE,
        ...     position=Position(line=0, column=4),
        ...     name="w",
        ... )
        >>> error.kind
        <ResolveErrorKind.UNDEFINED_VARIABLE: 'undefined_variable'>
    """

    kind: ResolveErrorKind
    position: Position
    name: str
