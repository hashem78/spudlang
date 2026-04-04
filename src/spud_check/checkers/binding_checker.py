from spud.core import Environment
from spud.core.types import SpudType
from spud.stage_six import Binding, FunctionDef, InlineFunctionDef
from spud_check.checkers.checker_protocol import INodeCheckerDispatch
from spud_check.type_errors import TypeError, TypeMismatchError
from spud_check.type_resolver import resolve_type
from spud_check.typed_nodes import TypedBinding


class BindingChecker:
    def __init__(self, dispatch: INodeCheckerDispatch):
        self._dispatch = dispatch

    def check(
        self,
        node: Binding,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> tuple[TypedBinding, Environment[SpudType]]:
        declared = resolve_type(node.type_annotation, errors)

        is_function = isinstance(node.value, FunctionDef | InlineFunctionDef)
        if is_function:
            env = env.with_binding(node.target.name, declared)

        typed_value, env = self._dispatch.dispatch(node.value, env, errors)

        if typed_value.resolved_type != declared:
            errors.append(
                TypeMismatchError(
                    position=node.position,
                    name=node.target.name,
                    expected=declared.kind,
                    actual=typed_value.resolved_type.kind,
                )
            )

        if not is_function:
            env = env.with_binding(node.target.name, declared)

        return TypedBinding(
            resolved_type=declared,
            position=node.position,
            end=node.end,
            target_name=node.target.name,
            type_annotation=node.type_annotation,
            value=typed_value,
        ), env
