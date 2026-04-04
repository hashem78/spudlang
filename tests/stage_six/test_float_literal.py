# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from spud.stage_six.binary_op import BinaryOp
from spud.stage_six.binding import Binding
from spud.stage_six.float_literal import FloatLiteral
from spud.stage_six.function_call import FunctionCall
from spud.stage_six.int_literal import IntLiteral
from spud.stage_six.program import Program
from tests.stage_six.helpers import parse


class TestFloatLiteralParsing:
    def test_standard_float(self):
        result = parse("3.14")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FloatLiteral)
        assert node.value == 3.14

    def test_zero_point_five(self):
        result = parse("0.5")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FloatLiteral)
        assert node.value == 0.5

    def test_trailing_dot(self):
        result = parse("3.")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FloatLiteral)
        assert node.value == 3.0

    def test_leading_dot(self):
        result = parse(".5")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FloatLiteral)
        assert node.value == 0.5

    def test_zero_dot_zero(self):
        result = parse("0.0")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FloatLiteral)
        assert node.value == 0.0

    def test_large_float(self):
        result = parse("9999.9999")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FloatLiteral)
        assert node.value == 9999.9999

    def test_float_not_int_literal(self):
        result = parse("1.5")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FloatLiteral)
        assert not isinstance(node, IntLiteral)

    def test_integer_still_produces_int_literal(self):
        result = parse("42")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, IntLiteral)
        assert not isinstance(node, FloatLiteral)
        assert node.value == 42


class TestFloatInExpressions:
    def test_float_as_left_operand(self):
        result = parse("1.5 + x")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert isinstance(node.left, FloatLiteral)
        assert node.left.value == 1.5

    def test_float_as_right_operand(self):
        result = parse("x + 2.5")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert isinstance(node.right, FloatLiteral)
        assert node.right.value == 2.5

    def test_float_both_operands(self):
        result = parse("1.1 + 2.2")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert isinstance(node.left, FloatLiteral)
        assert node.left.value == 1.1
        assert isinstance(node.right, FloatLiteral)
        assert node.right.value == 2.2

    def test_float_multiplication(self):
        result = parse("3.0 * 2.0")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "*"
        assert isinstance(node.left, FloatLiteral)
        assert node.left.value == 3.0
        assert isinstance(node.right, FloatLiteral)
        assert node.right.value == 2.0

    def test_float_and_integer_mixed(self):
        result = parse("1.5 + 2")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert isinstance(node.left, FloatLiteral)
        assert node.left.value == 1.5
        assert isinstance(node.right, IntLiteral)
        assert node.right.value == 2

    def test_float_in_nested_expression(self):
        result = parse("1.0 + 2.0 * 3.0")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "+"
        assert isinstance(node.left, FloatLiteral)
        assert node.left.value == 1.0
        assert isinstance(node.right, BinaryOp)
        assert node.right.operator == "*"
        assert isinstance(node.right.left, FloatLiteral)
        assert node.right.left.value == 2.0
        assert isinstance(node.right.right, FloatLiteral)
        assert node.right.right.value == 3.0

    def test_float_in_binding(self):
        result = parse("x : Float := 3.14")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.value, FloatLiteral)
        assert node.value.value == 3.14

    def test_float_as_function_arg(self):
        result = parse("f(1.5)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert len(node.args) == 1
        assert isinstance(node.args[0], FloatLiteral)
        assert node.args[0].value == 1.5

    def test_float_multiple_function_args(self):
        result = parse("lerp(0.0, 1.0)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert isinstance(node.args[0], FloatLiteral)
        assert node.args[0].value == 0.0
        assert isinstance(node.args[1], FloatLiteral)
        assert node.args[1].value == 1.0

    def test_trailing_dot_in_binding(self):
        result = parse("x : Float := 5.")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.value, FloatLiteral)
        assert node.value.value == 5.0

    def test_leading_dot_in_binding(self):
        result = parse("x : Float := .25")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.value, FloatLiteral)
        assert node.value.value == 0.25
