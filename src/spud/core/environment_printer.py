from spud.core.environment import Environment


def print_environment(env: Environment) -> None:
    """Print the full environment tree starting from *env*.

    Walks the tree **downward** via ``children`` links, printing
    each scope's bindings with indentation proportional to depth.

    :param env: The root environment (typically the global scope).

    Example output for ``double := (x) => double(2.0 * x)``::

        global
          double
          scope
            x
    """
    _print_scope(env, depth=0)


def _print_scope(env: Environment, depth: int) -> None:
    """Recursively print a scope and its children."""
    indent = "  " * depth
    label = "global" if depth == 0 else "scope"
    print(f"{indent}{label}")
    for name in env.bindings:
        print(f"{indent}  {name}")
    for child in env.children:
        _print_scope(child, depth + 1)
