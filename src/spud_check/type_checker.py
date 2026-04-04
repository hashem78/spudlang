from spud.core import Environment
from spud.core.types import (
    BoolType,
    ListType,
    SpudType,
    UnitType,
)
from spud.stage_six import (
    ForLoop,
    IfElse,
    Program,
)
from spud_check.checkers import NodeChecker
from spud_check.type_check_result import TypeCheckResult
from spud_check.type_errors import (
    BranchTypeMismatchError,
    ConditionNotBoolError,
    ElementTypeMismatchError,
    NotIterableError,
    TypeError,
)
from spud_check.type_resolver import resolve_type
from spud_check.typed_nodes import (
    TypedConditionBranch,
    TypedForLoop,
    TypedIfElse,
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

    def _check_if_else(
        self,
        node: IfElse,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> TypedIfElse:
        typed_branches: list[TypedConditionBranch] = []
        branch_types: list[SpudType] = []

        for branch in node.branches:
            typed_cond, _ = self._node_checker.dispatch(branch.condition, env, errors)
            if typed_cond.resolved_type != BoolType():
                errors.append(
                    ConditionNotBoolError(
                        position=branch.condition.position,
                        actual=typed_cond.resolved_type.kind,
                    )
                )

            child_env = env.child()
            typed_body: list[TypedNode] = []
            for stmt in branch.body:
                typed_stmt, child_env = self._node_checker.dispatch(stmt, child_env, errors)
                typed_body.append(typed_stmt)

            branch_type = typed_body[-1].resolved_type if typed_body else UnitType()
            branch_types.append(branch_type)
            typed_branches.append(
                TypedConditionBranch(
                    resolved_type=branch_type,
                    position=branch.position,
                    end=branch.end,
                    condition=typed_cond,
                    body=typed_body,
                )
            )

        typed_else: list[TypedNode] | None = None
        if node.else_body:
            child_env = env.child()
            typed_else = []
            for stmt in node.else_body:
                typed_stmt, child_env = self._node_checker.dispatch(stmt, child_env, errors)
                typed_else.append(typed_stmt)
            else_type = typed_else[-1].resolved_type if typed_else else UnitType()
            branch_types.append(else_type)

        if len(branch_types) >= 2:
            first = branch_types[0]
            for i, bt in enumerate(branch_types[1:], 1):
                if bt != first:
                    errors.append(
                        BranchTypeMismatchError(
                            position=node.position,
                            index=i,
                            expected=first.kind,
                            actual=bt.kind,
                        )
                    )

        result_type = branch_types[0] if branch_types else UnitType()
        return TypedIfElse(
            resolved_type=result_type,
            position=node.position,
            end=node.end,
            branches=typed_branches,
            else_body=typed_else,
        )

    def _check_for_loop(
        self,
        node: ForLoop,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> TypedForLoop:
        typed_iterable, _ = self._node_checker.dispatch(node.iterable, env, errors)
        var_type = resolve_type(node.variable_type, errors)

        if not isinstance(typed_iterable.resolved_type, ListType):
            errors.append(
                NotIterableError(
                    position=node.iterable.position,
                    actual=typed_iterable.resolved_type.kind,
                )
            )
        else:
            if typed_iterable.resolved_type.element != var_type:
                errors.append(
                    ElementTypeMismatchError(
                        position=node.variable.position,
                        name=node.variable.name,
                        expected=var_type.kind,
                        actual=typed_iterable.resolved_type.element.kind,
                    )
                )

        child_env = env.child()
        child_env = child_env.with_binding(node.variable.name, var_type)

        typed_body: list[TypedNode] = []
        for stmt in node.body:
            typed_stmt, child_env = self._node_checker.dispatch(stmt, child_env, errors)
            typed_body.append(typed_stmt)

        return TypedForLoop(
            resolved_type=UnitType(),
            position=node.position,
            end=node.end,
            variable_name=node.variable.name,
            variable_type=var_type,
            iterable=typed_iterable,
            body=typed_body,
        )
