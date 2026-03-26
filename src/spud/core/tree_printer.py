from spud.stage_five.stage_five_token import StageFiveToken


def print_tree(expressions: list[StageFiveToken]) -> None:
    for expr in expressions:
        _print_node(expr, prefix="", is_last=True, is_root=True)


def _print_node(expr: StageFiveToken, prefix: str, is_last: bool, is_root: bool) -> None:
    value = " ".join(t.value for t in expr.tokens)

    if is_root:
        print(f"EXPR {value}")
        child_prefix = ""
    else:
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}EXPR {value}")
        child_prefix = prefix + ("    " if is_last else "│   ")

    for i, child in enumerate(expr.children):
        _print_node(child, child_prefix, is_last=i == len(expr.children) - 1, is_root=False)
