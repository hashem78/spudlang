from dependency_injector import containers, providers

from spud.di import Container as CoreContainer
from spud_check.checkers.binary_op_checker import BinaryOpChecker
from spud_check.checkers.binding_checker import BindingChecker
from spud_check.checkers.for_loop_checker import ForLoopChecker
from spud_check.checkers.function_call_checker import FunctionCallChecker
from spud_check.checkers.function_def_checker import FunctionDefChecker
from spud_check.checkers.if_else_checker import IfElseChecker
from spud_check.checkers.inline_function_def_checker import InlineFunctionDefChecker
from spud_check.checkers.list_literal_checker import ListLiteralChecker
from spud_check.checkers.node_checker import NodeChecker
from spud_check.checkers.unary_op_checker import UnaryOpChecker
from spud_check.type_checker import TypeChecker


def build_type_checker() -> TypeChecker:
    """Wire the node checker dispatch graph and return a TypeChecker.

    Resolves the circular dependency between NodeChecker and the per-node
    checkers using the late-init pattern (mirrors _create_program_parser
    in spud.di.container).
    """
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
    return TypeChecker(node_checker=node_checker)


class CheckContainer(containers.DeclarativeContainer):
    core = providers.Container(CoreContainer)

    pipeline = core.pipeline

    checker = providers.Singleton(build_type_checker)
