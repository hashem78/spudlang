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
from spud_check.checkers.binary_op_checker import BinaryOpChecker
from spud_check.checkers.binding_checker import BindingChecker
from spud_check.checkers.for_loop_checker import ForLoopChecker
from spud_check.checkers.function_call_checker import FunctionCallChecker
from spud_check.checkers.function_def_checker import FunctionDefChecker
from spud_check.checkers.if_else_checker import IfElseChecker
from spud_check.checkers.inline_function_def_checker import InlineFunctionDefChecker
from spud_check.checkers.list_literal_checker import ListLiteralChecker
from spud_check.checkers.unary_op_checker import UnaryOpChecker
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


class NodeChecker:
    """Dispatches AST nodes to the appropriate per-node checker.

    Leaf nodes (literals, identifiers) are handled inline because they
    are trivial and need no dispatch injection. Composite nodes are
    routed to dedicated checker classes that recursively dispatch back
    through this instance.
    """

    def __init__(
        self,
        binding_checker: BindingChecker,
        binary_op_checker: BinaryOpChecker,
        unary_op_checker: UnaryOpChecker,
        function_call_checker: FunctionCallChecker,
        list_literal_checker: ListLiteralChecker,
        function_def_checker: FunctionDefChecker,
        inline_function_def_checker: InlineFunctionDefChecker,
        if_else_checker: IfElseChecker,
        for_loop_checker: ForLoopChecker,
    ):
        self._binding_checker = binding_checker
        self._binary_op_checker = binary_op_checker
        self._unary_op_checker = unary_op_checker
        self._function_call_checker = function_call_checker
        self._list_literal_checker = list_literal_checker
        self._function_def_checker = function_def_checker
        self._inline_function_def_checker = inline_function_def_checker
        self._if_else_checker = if_else_checker
        self._for_loop_checker = for_loop_checker

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
                return self._binding_checker.check(node, env, errors)
            case BinaryOp():
                return self._binary_op_checker.check(node, env, errors)
            case UnaryOp():
                return self._unary_op_checker.check(node, env, errors)
            case FunctionCall():
                return self._function_call_checker.check(node, env, errors)
            case FunctionDef():
                return self._function_def_checker.check(node, env, errors)
            case InlineFunctionDef():
                return self._inline_function_def_checker.check(node, env, errors)
            case IfElse():
                return self._if_else_checker.check(node, env, errors)
            case ForLoop():
                return self._for_loop_checker.check(node, env, errors)
            case ListLiteral():
                return self._list_literal_checker.check(node, env, errors)
            case _:
                return TypedUnitLiteral(resolved_type=UnitType(), position=node.position, end=node.end), env


def build_node_checker() -> NodeChecker:
    node_checker = NodeChecker.__new__(NodeChecker)
    binding_checker = BindingChecker(dispatch=node_checker)
    binary_op_checker = BinaryOpChecker(dispatch=node_checker)
    unary_op_checker = UnaryOpChecker(dispatch=node_checker)
    function_call_checker = FunctionCallChecker(dispatch=node_checker)
    list_literal_checker = ListLiteralChecker(dispatch=node_checker)
    function_def_checker = FunctionDefChecker(dispatch=node_checker)
    inline_function_def_checker = InlineFunctionDefChecker(dispatch=node_checker)
    if_else_checker = IfElseChecker(dispatch=node_checker)
    for_loop_checker = ForLoopChecker(dispatch=node_checker)
    node_checker.__init__(
        binding_checker=binding_checker,
        binary_op_checker=binary_op_checker,
        unary_op_checker=unary_op_checker,
        function_call_checker=function_call_checker,
        list_literal_checker=list_literal_checker,
        function_def_checker=function_def_checker,
        inline_function_def_checker=inline_function_def_checker,
        if_else_checker=if_else_checker,
        for_loop_checker=for_loop_checker,
    )
    return node_checker
