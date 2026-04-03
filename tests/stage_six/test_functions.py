from spud.stage_six.binary_op import BinaryOp
from spud.stage_six.binding import Binding
from spud.stage_six.function_call import FunctionCall
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.identifier import Identifier
from spud.stage_six.inline_function_def import InlineFunctionDef
from spud.stage_six.int_literal import IntLiteral
from spud.stage_six.program import Program
from spud.stage_six.unary_op import UnaryOp
from spud.stage_six.unit_literal import UnitLiteral
from tests.stage_six.helpers import parse


class TestFunctionDefs:
    def test_no_params(self):
        result = parse("f := () =>\n  42")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "f"
        fdef = node.value
        assert isinstance(fdef, FunctionDef)
        assert fdef.params == []
        assert len(fdef.body) == 1
        assert isinstance(fdef.body[0], IntLiteral)
        assert fdef.body[0].value == 42

    def test_one_param(self):
        result = parse("f := (x) =>\n  x + 1")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        fdef = node.value
        assert isinstance(fdef, FunctionDef)
        assert len(fdef.params) == 1
        assert fdef.params[0].name == "x"
        assert len(fdef.body) == 1
        assert isinstance(fdef.body[0], BinaryOp)
        assert fdef.body[0].operator == "+"

    def test_two_params(self):
        result = parse("add := (a, b) =>\n  a + b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "add"
        fdef = node.value
        assert isinstance(fdef, FunctionDef)
        assert len(fdef.params) == 2
        assert fdef.params[0].name == "a"
        assert fdef.params[1].name == "b"

    def test_multi_line_body(self):
        result = parse("f := (x) =>\n  y := x + 1\n  y")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        fdef = node.value
        assert isinstance(fdef, FunctionDef)
        assert len(fdef.body) == 2
        assert isinstance(fdef.body[0], Binding)
        assert fdef.body[0].target.name == "y"
        assert isinstance(fdef.body[1], Identifier)
        assert fdef.body[1].name == "y"

    def test_nested_function_def(self):
        result = parse("outer := (x) =>\n  inner := (y) =>\n    x + y\n  inner(1)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "outer"
        outer_def = node.value
        assert isinstance(outer_def, FunctionDef)
        assert len(outer_def.params) == 1
        assert outer_def.params[0].name == "x"
        assert len(outer_def.body) == 2
        inner_binding = outer_def.body[0]
        assert isinstance(inner_binding, Binding)
        assert inner_binding.target.name == "inner"
        inner_def = inner_binding.value
        assert isinstance(inner_def, FunctionDef)
        assert len(inner_def.params) == 1
        assert inner_def.params[0].name == "y"
        assert len(inner_def.body) == 1
        assert isinstance(inner_def.body[0], BinaryOp)
        call = outer_def.body[1]
        assert isinstance(call, FunctionCall)
        assert call.callee.name == "inner"
        assert len(call.args) == 1
        assert isinstance(call.args[0], IntLiteral)
        assert call.args[0].value == 1


class TestFunctionCalls:
    def test_no_args(self):
        result = parse("foo()")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert node.callee.name == "foo"
        assert node.args == []

    def test_one_arg(self):
        result = parse("foo(1)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert node.callee.name == "foo"
        assert len(node.args) == 1
        assert isinstance(node.args[0], IntLiteral)
        assert node.args[0].value == 1

    def test_two_args(self):
        result = parse("foo(1, 2)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert node.callee.name == "foo"
        assert len(node.args) == 2
        assert isinstance(node.args[0], IntLiteral)
        assert node.args[0].value == 1
        assert isinstance(node.args[1], IntLiteral)
        assert node.args[1].value == 2

    def test_expression_arg(self):
        result = parse("foo(a + b)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert len(node.args) == 1
        assert isinstance(node.args[0], BinaryOp)
        assert node.args[0].operator == "+"

    def test_nested_calls(self):
        result = parse("foo(bar(1))")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert node.callee.name == "foo"
        assert len(node.args) == 1
        inner = node.args[0]
        assert isinstance(inner, FunctionCall)
        assert inner.callee.name == "bar"
        assert len(inner.args) == 1
        assert isinstance(inner.args[0], IntLiteral)
        assert inner.args[0].value == 1

    def test_call_as_arg(self):
        result = parse("foo(bar(1), baz(2))")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert node.callee.name == "foo"
        assert len(node.args) == 2
        assert isinstance(node.args[0], FunctionCall)
        assert node.args[0].callee.name == "bar"
        assert isinstance(node.args[1], FunctionCall)
        assert node.args[1].callee.name == "baz"


class TestInlineFunctionDefs:
    def test_two_params(self):
        result = parse("(a, b) => a + b")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, InlineFunctionDef)
        assert len(node.params) == 2
        assert node.params[0].name == "a"
        assert node.params[1].name == "b"
        assert isinstance(node.body, BinaryOp)
        assert node.body.operator == "+"

    def test_single_param(self):
        result = parse("(a) => a")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, InlineFunctionDef)
        assert len(node.params) == 1
        assert node.params[0].name == "a"
        assert isinstance(node.body, Identifier)
        assert node.body.name == "a"

    def test_no_params(self):
        result = parse("() => 42")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, InlineFunctionDef)
        assert node.params == []
        assert isinstance(node.body, IntLiteral)
        assert node.body.value == 42

    def test_void_callback(self):
        result = parse("() => ()")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, InlineFunctionDef)
        assert node.params == []
        assert isinstance(node.body, UnitLiteral)

    def test_binding_inline_function(self):
        result = parse("add := (a, b) => a + b")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "add"
        assert isinstance(node.value, InlineFunctionDef)
        assert len(node.value.params) == 2
        assert isinstance(node.value.body, BinaryOp)

    def test_as_function_argument(self):
        result = parse("map(items, (x) => x + 1)")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert node.callee.name == "map"
        assert len(node.args) == 2
        assert isinstance(node.args[0], Identifier)
        assert isinstance(node.args[1], InlineFunctionDef)
        assert len(node.args[1].params) == 1
        assert isinstance(node.args[1].body, BinaryOp)

    def test_nested_inline_functions(self):
        result = parse("(f) => (x) => f(x)")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, InlineFunctionDef)
        assert len(node.params) == 1
        assert isinstance(node.body, InlineFunctionDef)
        assert len(node.body.params) == 1
        assert isinstance(node.body.body, FunctionCall)

    def test_inline_with_unary(self):
        result = parse("(x) => -x")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, InlineFunctionDef)
        assert isinstance(node.body, UnaryOp)
        assert node.body.operator == "-"


class TestUnitLiteral:
    def test_standalone(self):
        result = parse("()")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, UnitLiteral)

    def test_in_binding(self):
        result = parse("x := ()")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.value, UnitLiteral)

    def test_as_function_argument(self):
        result = parse("f(())")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert len(node.args) == 1
        assert isinstance(node.args[0], UnitLiteral)
