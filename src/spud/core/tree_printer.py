from typing import Protocol, Sequence

from spud.stage_four.stage_four_token import StageFourToken


class TreeNode(Protocol):
    @property
    def token_type(self) -> object: ...

    @property
    def tokens(self) -> Sequence[StageFourToken]: ...

    @property
    def children(self) -> Sequence["TreeNode"]: ...


def print_tree(expressions: Sequence[TreeNode]) -> None:
    for expr in expressions:
        _print_node(expr, prefix="", is_last=True, is_root=True)


def _print_node(expr: TreeNode, prefix: str, is_last: bool, is_root: bool) -> None:
    label = expr.token_type.name  # type: ignore[union-attr]
    value = " ".join(t.value for t in expr.tokens)

    if is_root:
        print(f"{label} {value}")
        child_prefix = ""
    else:
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{label} {value}")
        child_prefix = prefix + ("    " if is_last else "│   ")

    for i, child in enumerate(expr.children):
        _print_node(child, child_prefix, is_last=i == len(expr.children) - 1, is_root=False)
