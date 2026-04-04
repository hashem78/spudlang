from spud.core import Environment
from spud.core.types import ListType, SpudType, UnitType
from spud.stage_six import ForLoop
from spud_check.checkers.checker_protocol import INodeCheckerDispatch
from spud_check.type_errors import ElementTypeMismatchError, NotIterableError, TypeError
from spud_check.type_resolver import resolve_type
from spud_check.typed_nodes import TypedForLoop, TypedNode


class ForLoopChecker:
    def __init__(self, dispatch: INodeCheckerDispatch):
        self._dispatch = dispatch

    def check(
        self,
        node: ForLoop,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> tuple[TypedForLoop, Environment[SpudType]]:
        typed_iterable, _ = self._dispatch.dispatch(node.iterable, env, errors)
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
            typed_stmt, child_env = self._dispatch.dispatch(stmt, child_env, errors)
            typed_body.append(typed_stmt)

        return TypedForLoop(
            resolved_type=UnitType(),
            position=node.position,
            end=node.end,
            variable_name=node.variable.name,
            variable_type=var_type,
            iterable=typed_iterable,
            body=typed_body,
        ), env
