from spud.core import Environment
from spud.core.types import FunctionType, SpudType
from spud.stage_six import InlineFunctionDef
from spud_check.checkers.checker_protocol import INodeCheckerDispatch
from spud_check.type_errors import ReturnTypeMismatchError, TypeError
from spud_check.type_resolver import resolve_type
from spud_check.typed_nodes import TypedInlineFunctionDef, TypedParam


class InlineFunctionDefChecker:
    def __init__(self, dispatch: INodeCheckerDispatch):
        self._dispatch = dispatch

    def check(
        self,
        node: InlineFunctionDef,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> tuple[TypedInlineFunctionDef, Environment[SpudType]]:
        param_types: list[SpudType] = []
        typed_params: list[TypedParam] = []
        child_env = env.child()

        for p in node.params:
            pt = resolve_type(p.type_annotation, errors)
            param_types.append(pt)
            child_env = child_env.with_binding(p.name.name, pt)
            typed_params.append(
                TypedParam(
                    resolved_type=pt, position=p.name.position, end=p.name.end, name=p.name.name, declared_type=pt
                )
            )

        return_type = resolve_type(node.return_type, errors)
        typed_body, _ = self._dispatch.dispatch(node.body, child_env, errors)

        if typed_body.resolved_type != return_type:
            errors.append(
                ReturnTypeMismatchError(
                    position=node.position,
                    expected=return_type.kind,
                    actual=typed_body.resolved_type.kind,
                )
            )

        func_type = FunctionType(params=tuple(param_types), returns=return_type)
        return TypedInlineFunctionDef(
            resolved_type=func_type,
            position=node.position,
            end=node.end,
            params=typed_params,
            return_type=return_type,
            body=typed_body,
        ), env
