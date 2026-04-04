from spud.core import Environment
from spud.core.types import ListType, SpudType, UnitType
from spud.stage_six import ListLiteral
from spud_check.checkers.checker_protocol import INodeCheckerDispatch
from spud_check.type_errors import HeterogeneousListError, TypeError
from spud_check.typed_nodes import TypedListLiteral, TypedNode


class ListLiteralChecker:
    def __init__(self, dispatch: INodeCheckerDispatch):
        self._dispatch = dispatch

    def check(
        self,
        node: ListLiteral,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> tuple[TypedListLiteral, Environment[SpudType]]:
        typed_elements: list[TypedNode] = []
        for elem in node.elements:
            typed_elem, _ = self._dispatch.dispatch(elem, env, errors)
            typed_elements.append(typed_elem)

        if not typed_elements:
            return TypedListLiteral(
                resolved_type=ListType(element=UnitType()),
                position=node.position,
                end=node.end,
                elements=[],
            ), env

        first_type = typed_elements[0].resolved_type
        for i, te in enumerate(typed_elements[1:], 1):
            if te.resolved_type != first_type:
                errors.append(
                    HeterogeneousListError(
                        position=te.position,
                        index=i,
                        expected=first_type.kind,
                        actual=te.resolved_type.kind,
                    )
                )

        return TypedListLiteral(
            resolved_type=ListType(element=first_type),
            position=node.position,
            end=node.end,
            elements=typed_elements,
        ), env
