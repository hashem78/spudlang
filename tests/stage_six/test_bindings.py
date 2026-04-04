from spud.stage_six.binary_op import BinaryOp
from spud.stage_six.binding import Binding
from spud.stage_six.boolean_literal import BooleanLiteral
from spud.stage_six.function_call import FunctionCall
from spud.stage_six.identifier import Identifier
from spud.stage_six.int_literal import IntLiteral
from spud.stage_six.program import Program
from spud.stage_six.string_literal import StringLiteral
from tests.stage_six.helpers import parse


class TestBindings:
    def test_simple_binding(self):
        result = parse("x : Int := 5")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.target, Identifier)
        assert node.target.name == "x"
        assert isinstance(node.value, IntLiteral)
        assert node.value.value == 5

    def test_binding_to_expression(self):
        result = parse("x : Int := a + b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "x"
        assert isinstance(node.value, BinaryOp)
        assert node.value.operator == "+"

    def test_binding_to_string(self):
        result = parse('name : String := "spud"')
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "name"
        assert isinstance(node.value, StringLiteral)
        assert node.value.value == "spud"

    def test_binding_to_boolean(self):
        result = parse("flag : Bool := true")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "flag"
        assert isinstance(node.value, BooleanLiteral)
        assert node.value.value is True

    def test_binding_to_function_call(self):
        result = parse("x : Int := foo(1)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "x"
        assert isinstance(node.value, FunctionCall)
        assert node.value.callee.name == "foo"
        assert len(node.value.args) == 1
        assert isinstance(node.value.args[0], IntLiteral)
        assert node.value.args[0].value == 1

    def test_multiple_bindings(self):
        result = parse("x : Int := 1\ny : Int := 2")
        assert isinstance(result, Program)
        assert len(result.body) == 2
        first = result.body[0]
        second = result.body[1]
        assert isinstance(first, Binding)
        assert first.target.name == "x"
        assert isinstance(first.value, IntLiteral)
        assert first.value.value == 1
        assert isinstance(second, Binding)
        assert second.target.name == "y"
        assert isinstance(second.value, IntLiteral)
        assert second.value.value == 2
