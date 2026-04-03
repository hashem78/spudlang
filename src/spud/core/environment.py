from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Environment(BaseModel, Generic[T], frozen=True):
    """An immutable, generic scope container that forms a tree via parent links.

    Each environment holds a mapping of names to values and an optional
    reference to a parent scope.  Because the model is frozen, every
    mutation (adding a binding, creating a child) returns a **new**
    ``Environment`` — the original is never modified.

    The type parameter ``T`` determines what is stored in the bindings.
    Stage 7 uses ``Environment[ASTNode]`` to map names to the AST nodes
    that introduced them; a future type-checker could use
    ``Environment[Type]`` over the same tree structure.

    Example::

        >>> env = Environment[int]()
        >>> env = env.with_binding("x", 1)
        >>> child = env.child()
        >>> child = child.with_binding("y", 2)
        >>> child.lookup("y")
        2
        >>> child.lookup("x")   # walks up to parent
        1
        >>> env.lookup("y")     # not visible in parent
        None
    """

    bindings: dict[str, T] = {}
    """Name-to-value mapping for **this** scope only."""

    parent: "Environment[T] | None" = None
    """The enclosing scope, or ``None`` for the global scope."""

    children: tuple["Environment[T]", ...] = ()
    """Child scopes branching off from this environment."""

    def with_binding(self, name: str, value: T) -> "Environment[T]":
        """Return a copy of this environment with *name* bound to *value*.

        If *name* already exists in this scope, the returned copy will
        contain the new value (the caller is responsible for checking
        duplicates before calling).

        :param name: The binding name.
        :param value: The value to associate with *name*.
        :returns: A new ``Environment`` with the binding added.

        Example::

            >>> env = Environment[int]()
            >>> env2 = env.with_binding("x", 42)
            >>> env2.lookup("x")
            42
            >>> env.lookup("x")  # original unchanged
            None
        """
        return self.model_copy(update={"bindings": {**self.bindings, name: value}})

    def child(self) -> "Environment[T]":
        """Create a new empty child scope whose parent is this environment.

        :returns: A fresh ``Environment`` with ``parent=self`` and no
            bindings of its own.

        Example::

            >>> global_env = Environment[str]().with_binding("x", "hello")
            >>> func_env = global_env.child()
            >>> func_env.lookup("x")  # visible via parent
            'hello'
            >>> func_env.contains("x")  # not in this scope
            False
        """
        return Environment(parent=self)

    def with_child(self, child: "Environment[T]") -> "Environment[T]":
        """Return a copy of this environment with *child* appended.

        :param child: The child scope to attach.
        :returns: A new ``Environment`` with *child* in ``children``.
        """
        return self.model_copy(update={"children": (*self.children, child)})

    def lookup(self, name: str) -> T | None:
        """Search for *name* in this scope and all ancestor scopes.

        Walks the parent chain starting from ``self`` until the name is
        found or the root (global) scope is reached.

        :param name: The binding name to search for.
        :returns: The bound value, or ``None`` if the name is not
            defined in any reachable scope.

        Example::

            >>> root = Environment[int]().with_binding("a", 1)
            >>> mid = root.child().with_binding("b", 2)
            >>> leaf = mid.child()
            >>> leaf.lookup("a")  # found two levels up
            1
            >>> leaf.lookup("z")  # not defined anywhere
            None
        """
        if name in self.bindings:
            return self.bindings[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def contains(self, name: str) -> bool:
        """Check whether *name* is bound in **this** scope only.

        Unlike :meth:`lookup`, this does **not** walk the parent chain.
        Use this to detect duplicate bindings within the same scope.

        :param name: The binding name to check.
        :returns: ``True`` if *name* exists in this scope's bindings.

        Example::

            >>> env = Environment[int]().with_binding("x", 1)
            >>> child = env.child()
            >>> child.contains("x")
            False
            >>> env.contains("x")
            True
        """
        return name in self.bindings
