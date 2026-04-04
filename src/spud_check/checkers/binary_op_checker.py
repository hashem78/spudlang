from spud.core import Environment
from spud.core.types import SpudType, UnitType
from spud.stage_six import BinaryOp
from spud_check.checkers.checker_protocol import INodeCheckerDispatch
from spud_check.operator_types import BINARY_OP_TYPES
from spud_check.type_errors import OperatorTypeError, TypeError
from spud_check.typed_nodes import TypedBinaryOp


class BinaryOpChecker:
    def __init__(self, dispatch: INodeCheckerDispatch):
        self._dispatch = dispatch

    def check(
        self,
        node: BinaryOp,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> tuple[TypedBinaryOp, Environment[SpudType]]:
        typed_left, _ = self._dispatch.dispatch(node.left, env, errors)
        typed_right, _ = self._dispatch.dispatch(node.right, env, errors)

        key = (node.operator, typed_left.resolved_type.kind, typed_right.resolved_type.kind)
        result_type = BINARY_OP_TYPES.get(key)

        if result_type is None:
            errors.append(
                OperatorTypeError(
                    position=node.position,
                    operator=node.operator,
                    left=typed_left.resolved_type.kind,
                    right=typed_right.resolved_type.kind,
                )
            )
            result_type = UnitType()

        return TypedBinaryOp(
            resolved_type=result_type,
            position=node.position,
            end=node.end,
            left=typed_left,
            operator=node.operator,
            right=typed_right,
        ), env
