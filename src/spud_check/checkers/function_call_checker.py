from spud.core import Environment
from spud.core.types import FunctionType, SpudType, UnitType
from spud.stage_six import FunctionCall
from spud_check.checkers.checker_protocol import INodeCheckerDispatch
from spud_check.type_errors import (
    ArgumentCountMismatchError,
    ArgumentTypeMismatchError,
    NotCallableError,
    TypeError,
)
from spud_check.typed_nodes import TypedFunctionCall, TypedNode


class FunctionCallChecker:
    def __init__(self, dispatch: INodeCheckerDispatch):
        self._dispatch = dispatch

    def check(
        self,
        node: FunctionCall,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> tuple[TypedFunctionCall, Environment[SpudType]]:
        callee_type = env.lookup(node.callee.name)

        if callee_type is None or not isinstance(callee_type, FunctionType):
            if callee_type is not None:
                errors.append(
                    NotCallableError(
                        position=node.position,
                        name=node.callee.name,
                    )
                )
            return TypedFunctionCall(
                resolved_type=UnitType(),
                position=node.position,
                end=node.end,
                callee_name=node.callee.name,
                args=[self._dispatch.dispatch(a, env, errors)[0] for a in node.args],
            ), env

        if len(node.args) != len(callee_type.params):
            errors.append(
                ArgumentCountMismatchError(
                    position=node.position,
                    name=node.callee.name,
                    expected_count=len(callee_type.params),
                    actual_count=len(node.args),
                )
            )

        typed_args: list[TypedNode] = []
        for i, arg in enumerate(node.args):
            typed_arg, _ = self._dispatch.dispatch(arg, env, errors)
            typed_args.append(typed_arg)
            if i < len(callee_type.params) and typed_arg.resolved_type != callee_type.params[i]:
                errors.append(
                    ArgumentTypeMismatchError(
                        position=arg.position,
                        name=node.callee.name,
                        index=i,
                        expected=callee_type.params[i].kind,
                        actual=typed_arg.resolved_type.kind,
                    )
                )

        return TypedFunctionCall(
            resolved_type=callee_type.returns,
            position=node.position,
            end=node.end,
            callee_name=node.callee.name,
            args=typed_args,
        ), env
