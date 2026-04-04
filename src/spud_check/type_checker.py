from spud.core import Environment
from spud.core.types import (
    SpudType,
    UnitType,
)
from spud.stage_six import (
    Program,
)
from spud_check.checkers import NodeChecker
from spud_check.type_check_result import TypeCheckResult
from spud_check.type_errors import (
    TypeError,
)
from spud_check.typed_nodes import (
    TypedNode,
    TypedProgram,
)


class TypeChecker:
    """Type checker for spud programs.

    Single-pass AST walk that threads an Environment[SpudType]
    through the tree. Resolves type annotations, checks consistency,
    and builds a parallel typed AST.
    """

    def __init__(self, node_checker: "NodeChecker | None" = None):
        from spud_check.checkers import build_node_checker

        self._node_checker = node_checker if node_checker is not None else build_node_checker(self)

    def check(self, program: Program) -> TypeCheckResult:
        errors: list[TypeError] = []
        env: Environment[SpudType] = Environment()
        typed_body: list[TypedNode] = []

        for node in program.body:
            typed_node, env = self._node_checker.dispatch(node, env, errors)
            typed_body.append(typed_node)

        typed_program = TypedProgram(
            resolved_type=UnitType(),
            position=program.position,
            end=program.end,
            body=typed_body,
        )
        return TypeCheckResult(errors=errors, typed_program=typed_program)
