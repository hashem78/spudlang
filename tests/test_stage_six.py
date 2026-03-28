# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from typing import Generator

import structlog

from spud.di.stage_four_trie import create_stage_four_trie
from spud.di.stage_two_trie import create_stage_two_trie
from spud.stage_five.stage_five import StageFive
from spud.stage_four.stage_four import StageFour
from spud.stage_one.stage_one import StageOne
from spud.stage_six.binary_op import BinaryOp
from spud.stage_six.binding import Binding
from spud.stage_six.boolean_literal import BooleanLiteral
from spud.stage_six.condition_branch import ConditionBranch
from spud.stage_six.for_loop import ForLoop
from spud.stage_six.function_call import FunctionCall
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.identifier import Identifier
from spud.stage_six.if_else import IfElse
from spud.stage_six.numeric_literal import NumericLiteral
from spud.stage_six.parsers.binding_parser import BindingParser
from spud.stage_six.parsers.block_parser import BlockParser
from spud.stage_six.parsers.expression_parser import ExpressionParser
from spud.stage_six.parsers.for_loop_parser import ForLoopParser
from spud.stage_six.parsers.function_def_parser import FunctionDefParser
from spud.stage_six.parsers.if_else_parser import IfElseParser
from spud.stage_six.parsers.program_parser import ProgramParser
from spud.stage_six.parsers.statement_parser import StatementParser
from spud.stage_six.program import Program
from spud.stage_six.raw_string_literal import RawStringLiteral
from spud.stage_six.string_literal import StringLiteral
from spud.stage_six.token_stream import TokenStream
from spud.stage_three.stage_three import StageThree
from spud.stage_two.stage_two import StageTwo


class _StringReader:
    def __init__(self, text: str):
        self._text = text

    def read(self) -> Generator[str, None, None]:
        for char in self._text:
            yield char


def _create_program_parser() -> dict:
    expression = ExpressionParser()
    block = BlockParser.__new__(BlockParser)
    function_def = FunctionDefParser(block_parser=block)
    binding = BindingParser(expression_parser=expression, function_def_parser=function_def)
    if_else = IfElseParser(expression_parser=expression, block_parser=block)
    for_loop = ForLoopParser(expression_parser=expression, block_parser=block)
    statement = StatementParser(
        expression_parser=expression,
        binding_parser=binding,
        if_else_parser=if_else,
        for_loop_parser=for_loop,
    )
    block.__init__(statement_parser=statement)
    program = ProgramParser(statement_parser=statement)
    return {"program_parser": program}


def _parse(text: str) -> Program:
    reader = _StringReader(text)
    s1 = StageOne(reader)
    s2 = StageTwo(s1, create_stage_two_trie(), structlog.get_logger())
    s3 = StageThree(s2, structlog.get_logger())
    s4 = StageFour(s3, create_stage_four_trie(), structlog.get_logger())
    s5 = StageFive(s4, structlog.get_logger())
    tokens = list(s5.parse())
    stream = TokenStream(tokens)
    parsers = _create_program_parser()
    return parsers["program_parser"].parse(stream)


# ── Empty Input ────────────────────────────────────────────────────


class TestEmptyInput:
    def test_empty_string(self):
        result = _parse("")
        assert isinstance(result, Program)
        assert result.body == []

    def test_only_newlines(self):
        result = _parse("\n\n\n")
        assert isinstance(result, Program)
        assert result.body == []


# ── Literals ───────────────────────────────────────────────────────


class TestLiterals:
    def test_numeric(self):
        result = _parse("42")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, NumericLiteral)
        assert node.value == 42

    def test_zero(self):
        result = _parse("0")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, NumericLiteral)
        assert node.value == 0

    def test_string(self):
        result = _parse('"hello"')
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, StringLiteral)
        assert node.value == "hello"

    def test_raw_string(self):
        result = _parse("`raw`")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, RawStringLiteral)
        assert node.value == "raw"

    def test_boolean_true(self):
        result = _parse("true")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, BooleanLiteral)
        assert node.value is True

    def test_boolean_false(self):
        result = _parse("false")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, BooleanLiteral)
        assert node.value is False


# ── Identifiers ────────────────────────────────────────────────────


class TestIdentifiers:
    def test_bare_identifier(self):
        result = _parse("x")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, Identifier)
        assert node.name == "x"

    def test_multi_char_identifier(self):
        result = _parse("foo")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, Identifier)
        assert node.name == "foo"


# ── Binary Operations ─────────────────────────────────────────────


class TestBinaryOperations:
    def test_simple_add(self):
        result = _parse("a + b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "+"
        assert isinstance(node.left, Identifier)
        assert node.left.name == "a"
        assert isinstance(node.right, Identifier)
        assert node.right.name == "b"

    def test_precedence_mul_over_add(self):
        result = _parse("a + b * c")
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
        result = _parse("a + b + c")
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
        result = _parse("a - b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "-"

    def test_multiplication(self):
        result = _parse("a * b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "*"

    def test_division(self):
        result = _parse("a / b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "/"

    def test_modulo(self):
        result = _parse("a % b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "%"

    def test_equals(self):
        result = _parse("a == b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "=="

    def test_not_equals(self):
        result = _parse("a != b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "!="

    def test_less_than(self):
        result = _parse("a < b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "<"

    def test_greater_than(self):
        result = _parse("a > b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == ">"

    def test_less_than_or_equal(self):
        result = _parse("a <= b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "<="

    def test_greater_than_or_equal(self):
        result = _parse("a >= b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == ">="

    def test_logical_and(self):
        result = _parse("a && b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "&&"
        assert isinstance(node.left, Identifier)
        assert isinstance(node.right, Identifier)

    def test_logical_or(self):
        result = _parse("a || b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "||"
        assert isinstance(node.left, Identifier)
        assert isinstance(node.right, Identifier)

    def test_or_lower_precedence_than_and(self):
        result = _parse("a || b && c")
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
        result = _parse("a > b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == ">"
        assert isinstance(node.left, Identifier)
        assert isinstance(node.right, Identifier)

    def test_parenthesized_grouping(self):
        result = _parse("(a + b) * c")
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
        result = _parse("((a))")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Identifier)
        assert node.name == "a"

    def test_unary_minus(self):
        result = _parse("-x")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "-"
        assert isinstance(node.left, NumericLiteral)
        assert node.left.value == 0
        assert isinstance(node.right, Identifier)
        assert node.right.name == "x"

    def test_double_negation(self):
        result = _parse("--x")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "-"
        assert isinstance(node.left, NumericLiteral)
        assert node.left.value == 0
        assert isinstance(node.right, BinaryOp)
        assert node.right.operator == "-"
        assert isinstance(node.right.left, NumericLiteral)
        assert node.right.left.value == 0
        assert isinstance(node.right.right, Identifier)
        assert node.right.right.name == "x"

    def test_complex_expression(self):
        result = _parse("a + b * c - d / e")
        assert isinstance(result, Program)
        # Should parse as: (a + (b * c)) - (d / e)
        # Due to left-assoc at +/- level: ((a + (b*c)) - (d/e))
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


# ── Bindings ──────────────────────────────────────────────────────


class TestBindings:
    def test_simple_binding(self):
        result = _parse("x := 5")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.target, Identifier)
        assert node.target.name == "x"
        assert isinstance(node.value, NumericLiteral)
        assert node.value.value == 5

    def test_binding_to_expression(self):
        result = _parse("x := a + b")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "x"
        assert isinstance(node.value, BinaryOp)
        assert node.value.operator == "+"

    def test_binding_to_string(self):
        result = _parse('name := "spud"')
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "name"
        assert isinstance(node.value, StringLiteral)
        assert node.value.value == "spud"

    def test_binding_to_boolean(self):
        result = _parse("flag := true")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "flag"
        assert isinstance(node.value, BooleanLiteral)
        assert node.value.value is True

    def test_binding_to_function_call(self):
        result = _parse("x := foo(1)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "x"
        assert isinstance(node.value, FunctionCall)
        assert node.value.callee.name == "foo"
        assert len(node.value.args) == 1
        assert isinstance(node.value.args[0], NumericLiteral)
        assert node.value.args[0].value == 1

    def test_multiple_bindings(self):
        result = _parse("x := 1\ny := 2")
        assert isinstance(result, Program)
        assert len(result.body) == 2
        first = result.body[0]
        second = result.body[1]
        assert isinstance(first, Binding)
        assert first.target.name == "x"
        assert isinstance(first.value, NumericLiteral)
        assert first.value.value == 1
        assert isinstance(second, Binding)
        assert second.target.name == "y"
        assert isinstance(second.value, NumericLiteral)
        assert second.value.value == 2


# ── Function Definitions ─────────────────────────────────────────


class TestFunctionDefs:
    def test_no_params(self):
        result = _parse("f := () =>\n  42")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "f"
        fdef = node.value
        assert isinstance(fdef, FunctionDef)
        assert fdef.params == []
        assert len(fdef.body) == 1
        assert isinstance(fdef.body[0], NumericLiteral)
        assert fdef.body[0].value == 42

    def test_one_param(self):
        result = _parse("f := (x) =>\n  x + 1")
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
        result = _parse("add := (a, b) =>\n  a + b")
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
        result = _parse("f := (x) =>\n  y := x + 1\n  y")
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
        result = _parse("outer := (x) =>\n  inner := (y) =>\n    x + y\n  inner(1)")
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
        assert isinstance(call.args[0], NumericLiteral)
        assert call.args[0].value == 1


# ── Function Calls ────────────────────────────────────────────────


class TestFunctionCalls:
    def test_no_args(self):
        result = _parse("foo()")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert node.callee.name == "foo"
        assert node.args == []

    def test_one_arg(self):
        result = _parse("foo(1)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert node.callee.name == "foo"
        assert len(node.args) == 1
        assert isinstance(node.args[0], NumericLiteral)
        assert node.args[0].value == 1

    def test_two_args(self):
        result = _parse("foo(1, 2)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert node.callee.name == "foo"
        assert len(node.args) == 2
        assert isinstance(node.args[0], NumericLiteral)
        assert node.args[0].value == 1
        assert isinstance(node.args[1], NumericLiteral)
        assert node.args[1].value == 2

    def test_expression_arg(self):
        result = _parse("foo(a + b)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert len(node.args) == 1
        assert isinstance(node.args[0], BinaryOp)
        assert node.args[0].operator == "+"

    def test_nested_calls(self):
        result = _parse("foo(bar(1))")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert node.callee.name == "foo"
        assert len(node.args) == 1
        inner = node.args[0]
        assert isinstance(inner, FunctionCall)
        assert inner.callee.name == "bar"
        assert len(inner.args) == 1
        assert isinstance(inner.args[0], NumericLiteral)
        assert inner.args[0].value == 1

    def test_call_as_arg(self):
        result = _parse("foo(bar(1), baz(2))")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert node.callee.name == "foo"
        assert len(node.args) == 2
        assert isinstance(node.args[0], FunctionCall)
        assert node.args[0].callee.name == "bar"
        assert isinstance(node.args[1], FunctionCall)
        assert node.args[1].callee.name == "baz"


# ── If/Else ───────────────────────────────────────────────────────


class TestIfElse:
    def test_if_only(self):
        result = _parse('if x > 0\n  "positive"')
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, IfElse)
        assert len(node.branches) == 1
        assert node.else_body is None
        branch = node.branches[0]
        assert isinstance(branch, ConditionBranch)
        assert isinstance(branch.condition, BinaryOp)
        assert branch.condition.operator == ">"
        assert len(branch.body) == 1
        assert isinstance(branch.body[0], StringLiteral)
        assert branch.body[0].value == "positive"

    def test_if_else(self):
        result = _parse('if x > 0\n  "positive"\nelse\n  "negative"')
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, IfElse)
        assert len(node.branches) == 1
        assert node.else_body is not None
        assert len(node.else_body) == 1
        assert isinstance(node.else_body[0], StringLiteral)
        assert node.else_body[0].value == "negative"

    def test_if_elif_else(self):
        result = _parse('if x > 0\n  "positive"\nelif x == 0\n  "zero"\nelse\n  "negative"')
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, IfElse)
        assert len(node.branches) == 2
        assert node.branches[0].condition.operator == ">"
        assert isinstance(node.branches[0].body[0], StringLiteral)
        assert node.branches[0].body[0].value == "positive"
        assert node.branches[1].condition.operator == "=="
        assert isinstance(node.branches[1].body[0], StringLiteral)
        assert node.branches[1].body[0].value == "zero"
        assert node.else_body is not None
        assert isinstance(node.else_body[0], StringLiteral)
        assert node.else_body[0].value == "negative"

    def test_multiple_elif(self):
        text = 'if x > 2\n  "a"\nelif x > 1\n  "b"\nelif x > 0\n  "c"\nelif x == 0\n  "d"\nelse\n  "e"'
        result = _parse(text)
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, IfElse)
        assert len(node.branches) == 4
        assert node.else_body is not None

    def test_nested_if(self):
        result = _parse('if a\n  if b\n    "both"')
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, IfElse)
        assert len(node.branches) == 1
        inner = node.branches[0].body[0]
        assert isinstance(inner, IfElse)
        assert len(inner.branches) == 1
        assert isinstance(inner.branches[0].body[0], StringLiteral)
        assert inner.branches[0].body[0].value == "both"

    def test_complex_condition(self):
        result = _parse('if a > 0 && b < 10\n  "ok"')
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, IfElse)
        cond = node.branches[0].condition
        assert isinstance(cond, BinaryOp)
        assert cond.operator == "&&"
        assert isinstance(cond.left, BinaryOp)
        assert cond.left.operator == ">"
        assert isinstance(cond.right, BinaryOp)
        assert cond.right.operator == "<"


# ── For Loop ──────────────────────────────────────────────────────


class TestForLoop:
    def test_simple(self):
        result = _parse("for i in items\n  process(i)")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, ForLoop)
        assert isinstance(node.variable, Identifier)
        assert node.variable.name == "i"
        assert isinstance(node.iterable, Identifier)
        assert node.iterable.name == "items"
        assert len(node.body) == 1
        assert isinstance(node.body[0], FunctionCall)
        assert node.body[0].callee.name == "process"

    def test_function_call_iterable(self):
        result = _parse("for i in range(10)\n  i")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, ForLoop)
        assert isinstance(node.iterable, FunctionCall)
        assert node.iterable.callee.name == "range"
        assert len(node.iterable.args) == 1
        assert isinstance(node.iterable.args[0], NumericLiteral)
        assert node.iterable.args[0].value == 10

    def test_nested_for(self):
        result = _parse("for i in a\n  for j in b\n    i + j")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, ForLoop)
        assert node.variable.name == "i"
        assert len(node.body) == 1
        inner = node.body[0]
        assert isinstance(inner, ForLoop)
        assert inner.variable.name == "j"
        assert len(inner.body) == 1
        assert isinstance(inner.body[0], BinaryOp)
        assert inner.body[0].operator == "+"

    def test_multi_line_body(self):
        result = _parse("for i in items\n  x := i + 1\n  print(x)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, ForLoop)
        assert len(node.body) == 2
        assert isinstance(node.body[0], Binding)
        assert node.body[0].target.name == "x"
        assert isinstance(node.body[1], FunctionCall)
        assert node.body[1].callee.name == "print"


# ── Complex Programs ──────────────────────────────────────────────


class TestComplexPrograms:
    def test_binding_function_def_call(self):
        text = "add := (a, b) =>\n  a + b\nresult := add(1, 2)"
        result = _parse(text)
        assert isinstance(result, Program)
        assert len(result.body) == 2
        assert isinstance(result.body[0], Binding)
        assert isinstance(result.body[0].value, FunctionDef)
        assert isinstance(result.body[1], Binding)
        assert isinstance(result.body[1].value, FunctionCall)
        assert result.body[1].value.callee.name == "add"

    def test_function_with_if_else_body(self):
        text = 'classify := (x) =>\n  if x > 0\n    "positive"\n  else\n    "negative"'
        result = _parse(text)
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        fdef = node.value
        assert isinstance(fdef, FunctionDef)
        assert len(fdef.body) == 1
        assert isinstance(fdef.body[0], IfElse)
        assert len(fdef.body[0].branches) == 1
        assert fdef.body[0].else_body is not None

    def test_function_with_for_loop_body(self):
        text = "looper := (items) =>\n  for i in items\n    process(i)"
        result = _parse(text)
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        fdef = node.value
        assert isinstance(fdef, FunctionDef)
        assert len(fdef.body) == 1
        assert isinstance(fdef.body[0], ForLoop)

    def test_deeply_nested(self):
        text = "nested := (n) =>\n  for i in range(n)\n    if i > 5\n      print(i)"
        result = _parse(text)
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        fdef = node.value
        assert isinstance(fdef, FunctionDef)
        assert len(fdef.body) == 1
        for_loop = fdef.body[0]
        assert isinstance(for_loop, ForLoop)
        assert len(for_loop.body) == 1
        if_else = for_loop.body[0]
        assert isinstance(if_else, IfElse)
        assert len(if_else.branches) == 1
        call = if_else.branches[0].body[0]
        assert isinstance(call, FunctionCall)
        assert call.callee.name == "print"

    def test_multiple_top_level_statements(self):
        text = 'x := 42\ngreet := (name) =>\n  print(name)\nfor i in range(x)\n  greet("hello")\nif x > 0\n  "positive"'
        result = _parse(text)
        assert isinstance(result, Program)
        assert len(result.body) == 4
        assert isinstance(result.body[0], Binding)
        assert isinstance(result.body[1], Binding)
        assert isinstance(result.body[1].value, FunctionDef)
        assert isinstance(result.body[2], ForLoop)
        assert isinstance(result.body[3], IfElse)

    def test_program_spud_pattern(self):
        text = 'nested := (n) =>\n  for i in range(n)\n    if i > 5\n      "big"\n    else\n      "small"'
        result = _parse(text)
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "nested"
        fdef = node.value
        assert isinstance(fdef, FunctionDef)
        assert len(fdef.params) == 1
        assert fdef.params[0].name == "n"
        assert len(fdef.body) == 1
        for_loop = fdef.body[0]
        assert isinstance(for_loop, ForLoop)
        assert for_loop.variable.name == "i"
        assert isinstance(for_loop.iterable, FunctionCall)
        assert for_loop.iterable.callee.name == "range"
        assert len(for_loop.body) == 1
        if_else = for_loop.body[0]
        assert isinstance(if_else, IfElse)
        assert len(if_else.branches) == 1
        assert if_else.branches[0].condition.operator == ">"
        assert isinstance(if_else.branches[0].body[0], StringLiteral)
        assert if_else.branches[0].body[0].value == "big"
        assert if_else.else_body is not None
        assert isinstance(if_else.else_body[0], StringLiteral)
        assert if_else.else_body[0].value == "small"


# ── Edge Cases ────────────────────────────────────────────────────


class TestEdgeCases:
    def test_single_expression_program(self):
        result = _parse("42")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        assert isinstance(result.body[0], NumericLiteral)
        assert result.body[0].value == 42

    def test_function_call_as_statement(self):
        result = _parse('print("hello")')
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert node.callee.name == "print"
        assert len(node.args) == 1
        assert isinstance(node.args[0], StringLiteral)
        assert node.args[0].value == "hello"

    def test_all_precedence_levels(self):
        result = _parse("a || b && c == d + e * f")
        assert isinstance(result, Program)
        # ||
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "||"
        assert isinstance(node.left, Identifier)
        assert node.left.name == "a"
        # &&
        rhs = node.right
        assert isinstance(rhs, BinaryOp)
        assert rhs.operator == "&&"
        assert isinstance(rhs.left, Identifier)
        assert rhs.left.name == "b"
        # ==
        rhs2 = rhs.right
        assert isinstance(rhs2, BinaryOp)
        assert rhs2.operator == "=="
        assert isinstance(rhs2.left, Identifier)
        assert rhs2.left.name == "c"
        # +
        rhs3 = rhs2.right
        assert isinstance(rhs3, BinaryOp)
        assert rhs3.operator == "+"
        assert isinstance(rhs3.left, Identifier)
        assert rhs3.left.name == "d"
        # *
        rhs4 = rhs3.right
        assert isinstance(rhs4, BinaryOp)
        assert rhs4.operator == "*"
        assert isinstance(rhs4.left, Identifier)
        assert rhs4.left.name == "e"
        assert isinstance(rhs4.right, Identifier)
        assert rhs4.right.name == "f"

    def test_binding_to_grouped_expression(self):
        result = _parse("x := (a + b)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "x"
        assert isinstance(node.value, BinaryOp)
        assert node.value.operator == "+"


# ── Parse Errors ──────────────────────────────────────────────────


class TestParseErrors:
    def test_unexpected_token_walrus_at_start(self):
        result = _parse(":= 5")
        assert len(result.errors) > 0

    def test_missing_closing_paren(self):
        result = _parse("foo(1")
        assert len(result.errors) > 0

    def test_missing_block_after_if(self):
        result = _parse("if true")
        assert len(result.errors) > 0
