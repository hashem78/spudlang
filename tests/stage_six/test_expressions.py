from spud.stage_six.binary_op import BinaryOp
from spud.stage_six.binding import Binding
from spud.stage_six.function_call import FunctionCall
from spud.stage_six.identifier import Identifier
from spud.stage_six.inline_function_def import InlineFunctionDef
from spud.stage_six.list_literal import ListLiteral
from spud.stage_six.numeric_literal import NumericLiteral
from spud.stage_six.program import Program
from spud.stage_six.string_literal import StringLiteral
from spud.stage_six.unary_op import UnaryOp
from tests.stage_six.helpers import parse


class TestBinaryOperations:
    def test_simple_add(self):
        result = parse("a + b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "+"
        assert isinstance(node.left, Identifier)
        assert node.left.name == "a"
        assert isinstance(node.right, Identifier)
        assert node.right.name == "b"

    def test_precedence_mul_over_add(self):
        result = parse("a + b * c")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "+"
        assert isinstance(node.left, Identifier)
        assert node.left.name == "a"
        assert isinstance(node.right, BinaryOp)
        assert node.right.operator == "*"
        assert isinstance(node.right.left, Identifier)
        assert node.right.left.name == "b"
        assert isinstance(node.right.right, Identifier)
        assert node.right.right.name == "c"

    def test_left_associativity(self):
        result = parse("a + b + c")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "+"
        assert isinstance(node.left, BinaryOp)
        assert node.left.operator == "+"
        assert isinstance(node.left.left, Identifier)
        assert node.left.left.name == "a"
        assert isinstance(node.left.right, Identifier)
        assert node.left.right.name == "b"
        assert isinstance(node.right, Identifier)
        assert node.right.name == "c"

    def test_subtraction(self):
        result = parse("a - b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "-"

    def test_multiplication(self):
        result = parse("a * b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "*"

    def test_division(self):
        result = parse("a / b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "/"

    def test_modulo(self):
        result = parse("a % b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "%"

    def test_equals(self):
        result = parse("a == b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "=="

    def test_not_equals(self):
        result = parse("a != b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "!="

    def test_less_than(self):
        result = parse("a < b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "<"

    def test_greater_than(self):
        result = parse("a > b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == ">"

    def test_less_than_or_equal(self):
        result = parse("a <= b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "<="

    def test_greater_than_or_equal(self):
        result = parse("a >= b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == ">="

    def test_logical_and(self):
        result = parse("a && b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "&&"
        assert isinstance(node.left, Identifier)
        assert isinstance(node.right, Identifier)

    def test_logical_or(self):
        result = parse("a || b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "||"
        assert isinstance(node.left, Identifier)
        assert isinstance(node.right, Identifier)

    def test_or_lower_precedence_than_and(self):
        result = parse("a || b && c")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "||"
        assert isinstance(node.left, Identifier)
        assert node.left.name == "a"
        assert isinstance(node.right, BinaryOp)
        assert node.right.operator == "&&"
        assert isinstance(node.right.left, Identifier)
        assert node.right.left.name == "b"
        assert isinstance(node.right.right, Identifier)
        assert node.right.right.name == "c"

    def test_comparison_non_associative(self):
        result = parse("a > b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == ">"
        assert isinstance(node.left, Identifier)
        assert isinstance(node.right, Identifier)

    def test_parenthesized_grouping(self):
        result = parse("(a + b) * c")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "*"
        assert isinstance(node.left, BinaryOp)
        assert node.left.operator == "+"
        assert node.left.left.name == "a"
        assert node.left.right.name == "b"
        assert isinstance(node.right, Identifier)
        assert node.right.name == "c"

    def test_deeply_nested_parens(self):
        result = parse("((a))")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Identifier)
        assert node.name == "a"

    def test_unary_minus(self):
        result = parse("-x")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, UnaryOp)
        assert node.operator == "-"
        assert isinstance(node.operand, Identifier)
        assert node.operand.name == "x"

    def test_double_negation(self):
        result = parse("--x")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, UnaryOp)
        assert node.operator == "-"
        assert isinstance(node.operand, UnaryOp)
        assert node.operand.operator == "-"
        assert isinstance(node.operand.operand, Identifier)
        assert node.operand.operand.name == "x"

    def test_complex_expression(self):
        result = parse("a + b * c - d / e")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "-"
        assert isinstance(node.left, BinaryOp)
        assert node.left.operator == "+"
        assert isinstance(node.left.left, Identifier)
        assert node.left.left.name == "a"
        assert isinstance(node.left.right, BinaryOp)
        assert node.left.right.operator == "*"
        assert isinstance(node.right, BinaryOp)
        assert node.right.operator == "/"
        assert isinstance(node.right.left, Identifier)
        assert node.right.left.name == "d"
        assert isinstance(node.right.right, Identifier)
        assert node.right.right.name == "e"


class TestListLiteral:
    def test_empty_list(self):
        result = parse("[]")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, ListLiteral)
        assert node.elements == []

    def test_single_element(self):
        result = parse("[1]")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, ListLiteral)
        assert len(node.elements) == 1
        assert isinstance(node.elements[0], NumericLiteral)
        assert node.elements[0].value == 1

    def test_multiple_elements(self):
        result = parse("[1, 2, 3]")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, ListLiteral)
        assert len(node.elements) == 3
        assert all(isinstance(e, NumericLiteral) for e in node.elements)

    def test_mixed_expressions(self):
        result = parse('[1, "hello", true]')
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, ListLiteral)
        assert len(node.elements) == 3
        assert isinstance(node.elements[0], NumericLiteral)
        assert isinstance(node.elements[1], StringLiteral)

    def test_nested_lists(self):
        result = parse("[[1, 2], [3, 4]]")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, ListLiteral)
        assert len(node.elements) == 2
        assert isinstance(node.elements[0], ListLiteral)
        assert isinstance(node.elements[1], ListLiteral)
        assert len(node.elements[0].elements) == 2

    def test_expression_elements(self):
        result = parse("[a + b, max(1, 2)]")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, ListLiteral)
        assert len(node.elements) == 2
        assert isinstance(node.elements[0], BinaryOp)
        assert isinstance(node.elements[1], FunctionCall)

    def test_inline_function_element(self):
        result = parse("[(a, b) => a + b]")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, ListLiteral)
        assert len(node.elements) == 1
        assert isinstance(node.elements[0], InlineFunctionDef)

    def test_list_in_binding(self):
        result = parse("x := [1, 2, 3]")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.value, ListLiteral)
        assert len(node.value.elements) == 3

    def test_list_as_function_arg(self):
        result = parse("f([1, 2])")
        assert not result.errors
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert len(node.args) == 1
        assert isinstance(node.args[0], ListLiteral)
