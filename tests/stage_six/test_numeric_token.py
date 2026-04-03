# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from spud.stage_six.binary_op import BinaryOp
from spud.stage_six.binding import Binding
from spud.stage_six.function_call import FunctionCall
from spud.stage_six.identifier import Identifier
from spud.stage_six.numeric_literal import NumericLiteral
from spud.stage_six.program import Program
from tests.stage_six.helpers import parse


class TestNumericLiteralParsing:
    def test_single_digit(self):
        result = parse("1")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, NumericLiteral)
        assert node.value == 1

    def test_multi_digit(self):
        result = parse("100")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, NumericLiteral)
        assert node.value == 100

    def test_large_number(self):
        result = parse("9876543210")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, NumericLiteral)
        assert node.value == 9876543210

    def test_zero(self):
        result = parse("0")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, NumericLiteral)
        assert node.value == 0

    def test_numeric_not_identifier(self):
        result = parse("42")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, NumericLiteral)
        assert not isinstance(node, Identifier)

    def test_all_single_digits(self):
        for digit in range(10):
            result = parse(str(digit))
            assert isinstance(result, Program)
            node = result.body[0]
            assert isinstance(node, NumericLiteral)
            assert node.value == digit


class TestNumericInExpressions:
    def test_numeric_as_left_operand(self):
        result = parse("1 + x")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert isinstance(node.left, NumericLiteral)
        assert node.left.value == 1

    def test_numeric_as_right_operand(self):
        result = parse("x + 2")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert isinstance(node.right, NumericLiteral)
        assert node.right.value == 2

    def test_numeric_both_operands(self):
        result = parse("3 + 4")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert isinstance(node.left, NumericLiteral)
        assert node.left.value == 3
        assert isinstance(node.right, NumericLiteral)
        assert node.right.value == 4

    def test_numeric_multiplication(self):
        result = parse("6 * 7")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "*"
        assert isinstance(node.left, NumericLiteral)
        assert node.left.value == 6
        assert isinstance(node.right, NumericLiteral)
        assert node.right.value == 7

    def test_numeric_subtraction(self):
        result = parse("10 - 3")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "-"
        assert isinstance(node.left, NumericLiteral)
        assert node.left.value == 10
        assert isinstance(node.right, NumericLiteral)
        assert node.right.value == 3

    def test_numeric_division(self):
        result = parse("8 / 4")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "/"
        assert isinstance(node.left, NumericLiteral)
        assert node.left.value == 8

    def test_numeric_in_nested_expression(self):
        result = parse("1 + 2 * 3")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "+"
        assert isinstance(node.left, NumericLiteral)
        assert node.left.value == 1
        assert isinstance(node.right, BinaryOp)
        assert node.right.operator == "*"
        assert isinstance(node.right.left, NumericLiteral)
        assert node.right.left.value == 2
        assert isinstance(node.right.right, NumericLiteral)
        assert node.right.right.value == 3

    def test_numeric_in_binding(self):
        result = parse("x := 42")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.value, NumericLiteral)
        assert node.value.value == 42

    def test_numeric_as_function_arg(self):
        result = parse("f(99)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert len(node.args) == 1
        assert isinstance(node.args[0], NumericLiteral)
        assert node.args[0].value == 99

    def test_numeric_multiple_function_args(self):
        result = parse("add(1, 2)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert isinstance(node.args[0], NumericLiteral)
        assert node.args[0].value == 1
        assert isinstance(node.args[1], NumericLiteral)
        assert node.args[1].value == 2


class TestAlphanumericIsIdentifier:
    def test_alpha_digit_identifier(self):
        result = parse("x1")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Identifier)
        assert node.name == "x1"

    def test_digit_alpha_identifier(self):
        result = parse("x1y")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Identifier)
        assert node.name == "x1y"

    def test_multi_char_identifier_with_digits(self):
        result = parse("foo42")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Identifier)
        assert node.name == "foo42"
        assert not isinstance(node, NumericLiteral)
