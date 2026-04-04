from spud.core import Environment
from spud.core.types import BoolType, FloatType, IntType, SpudType, StringType, UnitType
from spud.stage_six import (
    ASTNode,
    BinaryOp,
    Binding,
    BooleanLiteral,
    FloatLiteral,
    ForLoop,
    FunctionCall,
    FunctionDef,
    Identifier,
    IfElse,
    InlineFunctionDef,
    IntLiteral,
    ListLiteral,
    RawStringLiteral,
    StringLiteral,
    UnaryOp,
    UnitLiteral,
)
from spud_check.type_errors import TypeError
from spud_check.typed_nodes import (
    TypedBooleanLiteral,
    TypedFloatLiteral,
    TypedIdentifier,
    TypedIntLiteral,
    TypedNode,
    TypedStringLiteral,
    TypedUnitLiteral,
)


class _TypeCheckerShim:
    """Adapter that delegates composite node checks back to TypeChecker's
    per-node methods. Used during the refactor while checker classes are
    being extracted incrementally. Deleted in the final commit.
    """

    def __init__(self, type_checker: "object"):
        self._tc = type_checker

    def check_binding(
        self, node: Binding, env: Environment[SpudType], errors: list[TypeError]
    ) -> tuple[TypedNode, Environment[SpudType]]:
        return self._tc._check_binding(node, env, errors)  # type: ignore[attr-defined]

    def check_binary_op(
        self, node: BinaryOp, env: Environment[SpudType], errors: list[TypeError]
    ) -> tuple[TypedNode, Environment[SpudType]]:
        return self._tc._check_binary_op(node, env, errors), env  # type: ignore[attr-defined]

    def check_unary_op(
        self, node: UnaryOp, env: Environment[SpudType], errors: list[TypeError]
    ) -> tuple[TypedNode, Environment[SpudType]]:
        return self._tc._check_unary_op(node, env, errors), env  # type: ignore[attr-defined]

    def check_function_call(
        self, node: FunctionCall, env: Environment[SpudType], errors: list[TypeError]
    ) -> tuple[TypedNode, Environment[SpudType]]:
        return self._tc._check_function_call(node, env, errors), env  # type: ignore[attr-defined]

    def check_function_def(
        self, node: FunctionDef, env: Environment[SpudType], errors: list[TypeError]
    ) -> tuple[TypedNode, Environment[SpudType]]:
        return self._tc._check_function_def(node, env, errors), env  # type: ignore[attr-defined]

    def check_inline_function_def(
        self, node: InlineFunctionDef, env: Environment[SpudType], errors: list[TypeError]
    ) -> tuple[TypedNode, Environment[SpudType]]:
        return self._tc._check_inline_function_def(node, env, errors), env  # type: ignore[attr-defined]

    def check_if_else(
        self, node: IfElse, env: Environment[SpudType], errors: list[TypeError]
    ) -> tuple[TypedNode, Environment[SpudType]]:
        return self._tc._check_if_else(node, env, errors), env  # type: ignore[attr-defined]

    def check_for_loop(
        self, node: ForLoop, env: Environment[SpudType], errors: list[TypeError]
    ) -> tuple[TypedNode, Environment[SpudType]]:
        return self._tc._check_for_loop(node, env, errors), env  # type: ignore[attr-defined]

    def check_list_literal(
        self, node: ListLiteral, env: Environment[SpudType], errors: list[TypeError]
    ) -> tuple[TypedNode, Environment[SpudType]]:
        return self._tc._check_list_literal(node, env, errors), env  # type: ignore[attr-defined]


class NodeChecker:
    """Dispatches AST nodes to the appropriate per-node checker.

    Leaf nodes (literals, identifiers) are handled inline because they
    are trivial and need no dispatch injection. Composite nodes are
    routed to dedicated checker classes that recursively dispatch back
    through this instance.
    """

    def __init__(self, shim: _TypeCheckerShim):
        self._shim = shim

    def dispatch(
        self,
        node: ASTNode,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> tuple[TypedNode, Environment[SpudType]]:
        match node:
            case IntLiteral(value=value):
                return TypedIntLiteral(resolved_type=IntType(), position=node.position, end=node.end, value=value), env
            case FloatLiteral(value=value):
                return TypedFloatLiteral(
                    resolved_type=FloatType(), position=node.position, end=node.end, value=value
                ), env
            case StringLiteral(value=value) | RawStringLiteral(value=value):
                return TypedStringLiteral(
                    resolved_type=StringType(), position=node.position, end=node.end, value=value
                ), env
            case BooleanLiteral(value=value):
                return TypedBooleanLiteral(
                    resolved_type=BoolType(), position=node.position, end=node.end, value=value
                ), env
            case UnitLiteral():
                return TypedUnitLiteral(resolved_type=UnitType(), position=node.position, end=node.end), env
            case Identifier(name=name):
                resolved = env.lookup(name)
                resolved_type: SpudType = resolved if resolved is not None else UnitType()
                return TypedIdentifier(
                    resolved_type=resolved_type, position=node.position, end=node.end, name=name
                ), env
            case Binding():
                return self._shim.check_binding(node, env, errors)
            case BinaryOp():
                return self._shim.check_binary_op(node, env, errors)
            case UnaryOp():
                return self._shim.check_unary_op(node, env, errors)
            case FunctionCall():
                return self._shim.check_function_call(node, env, errors)
            case FunctionDef():
                return self._shim.check_function_def(node, env, errors)
            case InlineFunctionDef():
                return self._shim.check_inline_function_def(node, env, errors)
            case IfElse():
                return self._shim.check_if_else(node, env, errors)
            case ForLoop():
                return self._shim.check_for_loop(node, env, errors)
            case ListLiteral():
                return self._shim.check_list_literal(node, env, errors)
            case _:
                return TypedUnitLiteral(resolved_type=UnitType(), position=node.position, end=node.end), env


def build_node_checker(type_checker: object) -> NodeChecker:
    return NodeChecker(shim=_TypeCheckerShim(type_checker))
