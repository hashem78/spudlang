from spud_check.typed_nodes.typed_condition_branch import TypedConditionBranch
from spud_check.typed_nodes.typed_node import TypedNode


class TypedIfElse(TypedNode, frozen=True):
    branches: list[TypedConditionBranch]
    else_body: list[TypedNode] | None
