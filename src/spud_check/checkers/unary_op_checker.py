from spud.core import Environment
from spud.core.types import SpudType, UnitType
from spud.stage_six import UnaryOp
from spud_check.checkers.checker_protocol import INodeCheckerDispatch
from spud_check.operator_types import UNARY_OP_TYPES
from spud_check.type_errors import TypeError, UnaryOperatorTypeError
from spud_check.typed_nodes import TypedUnaryOp


class UnaryOpChecker:
    def __init__(self, dispatch: INodeCheckerDispatch):
        self._dispatch = dispatch

    def check(
        self,
        node: UnaryOp,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> tuple[TypedUnaryOp, Environment[SpudType]]:
        typed_operand, _ = self._dispatch.dispatch(node.operand, env, errors)

        key = (node.operator, typed_operand.resolved_type.kind)
        result_type = UNARY_OP_TYPES.get(key)

        if result_type is None:
            errors.append(
                UnaryOperatorTypeError(
                    position=node.position,
                    operator=node.operator,
                    operand=typed_operand.resolved_type.kind,
                )
            )
            result_type = UnitType()

        return TypedUnaryOp(
            resolved_type=result_type,
            position=node.position,
            end=node.end,
            operator=node.operator,
            operand=typed_operand,
        ), env
