from spud.core import Environment
from spud.core.types import BoolType, SpudType, UnitType
from spud.stage_six import IfElse
from spud_check.checkers.checker_protocol import INodeCheckerDispatch
from spud_check.type_errors import BranchTypeMismatchError, ConditionNotBoolError, TypeError
from spud_check.typed_nodes import TypedConditionBranch, TypedIfElse, TypedNode


class IfElseChecker:
    def __init__(self, dispatch: INodeCheckerDispatch):
        self._dispatch = dispatch

    def check(
        self,
        node: IfElse,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> tuple[TypedIfElse, Environment[SpudType]]:
        typed_branches: list[TypedConditionBranch] = []
        branch_types: list[SpudType] = []

        for branch in node.branches:
            typed_cond, _ = self._dispatch.dispatch(branch.condition, env, errors)
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
                typed_stmt, child_env = self._dispatch.dispatch(stmt, child_env, errors)
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
                typed_stmt, child_env = self._dispatch.dispatch(stmt, child_env, errors)
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
        ), env
