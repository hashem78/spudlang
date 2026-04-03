from spud.core.environment import Environment


def print_environment(env: Environment) -> None:
    """Print the scope chain from the global scope down to *env*.

    Collects the chain of environments from *env* up to the root
    (following ``parent`` links), reverses it so the global scope
    prints first, then prints each scope with its bindings indented
    by nesting depth.

    :param env: The innermost (leaf) environment to visualise.
        The entire ancestor chain up to the root will be printed.

    Example output for a program with ``x := 5`` at the top level
    and a function ``f`` whose body defines ``y``::

        global
          x
          f
          scope 1
            y
    """
    chain = _collect_chain(env)
    for depth, scope in enumerate(chain):
        indent = "  " * depth
        if depth == 0:
            print(f"{indent}global")
        else:
            print(f"{indent}scope {depth}")
        for name in scope.bindings:
            print(f"{indent}  {name}")


def _collect_chain(env: Environment) -> list[Environment]:
    """Walk ``parent`` links from *env* to the root and return the
    chain in root-first order.

    :param env: The starting (innermost) environment.
    :returns: A list of environments ordered from root (global) to
        *env*.
    """
    chain: list[Environment] = []
    current: Environment | None = env
    while current is not None:
        chain.append(current)
        current = current.parent
    chain.reverse()
    return chain
