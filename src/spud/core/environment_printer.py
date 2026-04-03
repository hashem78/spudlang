from spud.core.environment import Environment


def print_environment(env: Environment) -> None:
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
    chain: list[Environment] = []
    current: Environment | None = env
    while current is not None:
        chain.append(current)
        current = current.parent
    chain.reverse()
    return chain
