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
from spud.stage_six.stage_six import StageSix
from spud.stage_six.stage_six_token import StageSixToken
from spud.stage_six.stage_six_token_type import StageSixTokenType
from spud.stage_three.stage_three import StageThree
from spud.stage_two.stage_two import StageTwo


class _StringReader:
    def __init__(self, text: str):
        self._text = text

    def read(self) -> Generator[str, None, None]:
        for char in self._text:
            yield char


def _parse(text: str) -> list[StageSixToken]:
    reader = _StringReader(text)
    logger = structlog.get_logger()
    stage_one = StageOne(reader)
    stage_two = StageTwo(stage_one, create_stage_two_trie(), logger)
    stage_three = StageThree(stage_two, logger)
    stage_four = StageFour(stage_three, create_stage_four_trie(), logger)
    stage_five = StageFive(stage_four, logger)
    stage_six = StageSix(stage_five, logger)
    return list(stage_six.parse())


def _type(expr: StageSixToken) -> StageSixTokenType:
    return expr.token_type


def _child_types(expr: StageSixToken) -> list[StageSixTokenType]:
    return [c.token_type for c in expr.children]


def _values(expr: StageSixToken) -> str:
    return " ".join(t.value for t in expr.tokens)


# ── Literals ──────────────────────────────────────────────────────────


class TestStringLiteral:
    def test_double_quoted(self):
        exprs = _parse('"hello"')
        assert _type(exprs[0]) == StageSixTokenType.STRING_LITERAL
        assert exprs[0].children == []

    def test_single_quoted(self):
        exprs = _parse("'hello'")
        assert _type(exprs[0]) == StageSixTokenType.STRING_LITERAL

    def test_empty_string(self):
        exprs = _parse('""')
        assert _type(exprs[0]) == StageSixTokenType.STRING_LITERAL

    def test_string_with_spaces(self):
        exprs = _parse('"hello world"')
        assert _type(exprs[0]) == StageSixTokenType.STRING_LITERAL


class TestRawStringLiteral:
    def test_basic(self):
        exprs = _parse("`hello`")
        assert _type(exprs[0]) == StageSixTokenType.RAW_STRING_LITERAL
        assert exprs[0].children == []

    def test_multiline(self):
        exprs = _parse("`line1\nline2`")
        assert _type(exprs[0]) == StageSixTokenType.RAW_STRING_LITERAL


class TestNumericLiteral:
    def test_single_digit(self):
        exprs = _parse("5")
        assert _type(exprs[0]) == StageSixTokenType.NUMERIC_LITERAL

    def test_multi_digit(self):
        exprs = _parse("42")
        assert _type(exprs[0]) == StageSixTokenType.NUMERIC_LITERAL

    def test_zero(self):
        exprs = _parse("0")
        assert _type(exprs[0]) == StageSixTokenType.NUMERIC_LITERAL


class TestBooleanLiteral:
    def test_true(self):
        exprs = _parse("true")
        assert _type(exprs[0]) == StageSixTokenType.BOOLEAN_LITERAL

    def test_false(self):
        exprs = _parse("false")
        assert _type(exprs[0]) == StageSixTokenType.BOOLEAN_LITERAL


# ── Assignment ────────────────────────────────────────────────────────


class TestAssignment:
    def test_simple_assignment(self):
        exprs = _parse("x := 1")
        assert _type(exprs[0]) == StageSixTokenType.ASSIGNMENT
        assert len(exprs[0].children) == 2

    def test_target_is_expression(self):
        exprs = _parse("x := 1")
        assert _type(exprs[0].children[0]) == StageSixTokenType.EXPRESSION

    def test_value_is_numeric(self):
        exprs = _parse("x := 42")
        assert _type(exprs[0].children[1]) == StageSixTokenType.NUMERIC_LITERAL

    def test_value_is_string(self):
        exprs = _parse('name := "spud"')
        assert _type(exprs[0].children[1]) == StageSixTokenType.STRING_LITERAL

    def test_value_is_boolean(self):
        exprs = _parse("flag := true")
        assert _type(exprs[0].children[1]) == StageSixTokenType.BOOLEAN_LITERAL

    def test_value_is_binary_op(self):
        exprs = _parse("x := a + b")
        assert _type(exprs[0].children[1]) == StageSixTokenType.BINARY_OP

    def test_value_is_function_call(self):
        exprs = _parse("x := foo(1)")
        assert _type(exprs[0].children[1]) == StageSixTokenType.FUNCTION_CALL

    def test_assignment_with_function_def(self):
        exprs = _parse("f := (x) =>\n  x + 1")
        assert _type(exprs[0]) == StageSixTokenType.ASSIGNMENT
        assert _type(exprs[0].children[0]) == StageSixTokenType.EXPRESSION
        assert _type(exprs[0].children[1]) == StageSixTokenType.FUNCTION_DEF

    def test_function_def_gets_body_children(self):
        exprs = _parse("f := (x) =>\n  x + 1")
        func_def = exprs[0].children[1]
        assert len(func_def.children) >= 1

    def test_non_func_assignment_gets_body_children(self):
        exprs = _parse("x := 1\n  y")
        assert _type(exprs[0]) == StageSixTokenType.ASSIGNMENT
        assert len(exprs[0].children) >= 3


# ── Function Definition ──────────────────────────────────────────────


class TestFunctionDef:
    def test_standalone_function_def(self):
        exprs = _parse("(x) =>\n  x")
        assert _type(exprs[0]) == StageSixTokenType.FUNCTION_DEF

    def test_function_body_classified(self):
        exprs = _parse("f := (a, b) =>\n  result := a + b\n  result")
        func = exprs[0].children[1]
        assert _type(func) == StageSixTokenType.FUNCTION_DEF
        child_types = _child_types(func)
        assert StageSixTokenType.ASSIGNMENT in child_types
        assert StageSixTokenType.EXPRESSION in child_types

    def test_nested_function_body(self):
        exprs = _parse("f := (n) =>\n  for i in range(n)\n    process(i)")
        func = exprs[0].children[1]
        assert any(_type(c) == StageSixTokenType.FOR_LOOP for c in func.children)


# ── Function Call ────────────────────────────────────────────────────


class TestFunctionCall:
    def test_no_args(self):
        exprs = _parse("foo()")
        assert _type(exprs[0]) == StageSixTokenType.FUNCTION_CALL
        # Callee only, no args.
        assert len(exprs[0].children) == 1
        assert _type(exprs[0].children[0]) == StageSixTokenType.EXPRESSION

    def test_one_arg(self):
        exprs = _parse("foo(1)")
        assert _type(exprs[0]) == StageSixTokenType.FUNCTION_CALL
        assert len(exprs[0].children) == 2
        assert _type(exprs[0].children[1]) == StageSixTokenType.NUMERIC_LITERAL

    def test_two_args(self):
        exprs = _parse("foo(1, 2)")
        assert _type(exprs[0]) == StageSixTokenType.FUNCTION_CALL
        assert len(exprs[0].children) == 3

    def test_string_arg(self):
        exprs = _parse('greet("world")')
        assert _type(exprs[0]) == StageSixTokenType.FUNCTION_CALL
        assert _type(exprs[0].children[1]) == StageSixTokenType.STRING_LITERAL

    def test_expression_arg(self):
        exprs = _parse("foo(a + b)")
        assert _type(exprs[0]) == StageSixTokenType.FUNCTION_CALL
        assert _type(exprs[0].children[1]) == StageSixTokenType.BINARY_OP

    def test_callee_is_expression(self):
        exprs = _parse("foo(1)")
        assert _type(exprs[0].children[0]) == StageSixTokenType.EXPRESSION
        assert _values(exprs[0].children[0]) == "foo"

    def test_nested_function_call(self):
        exprs = _parse("foo(bar(1))")
        assert _type(exprs[0]) == StageSixTokenType.FUNCTION_CALL
        assert _type(exprs[0].children[1]) == StageSixTokenType.FUNCTION_CALL


# ── Binary Operation ─────────────────────────────────────────────────


class TestBinaryOp:
    def test_addition(self):
        exprs = _parse("a + b")
        assert _type(exprs[0]) == StageSixTokenType.BINARY_OP
        assert len(exprs[0].children) == 2

    def test_comparison(self):
        exprs = _parse("a == b")
        assert _type(exprs[0]) == StageSixTokenType.BINARY_OP

    def test_left_operand(self):
        exprs = _parse("a + b")
        assert _type(exprs[0].children[0]) == StageSixTokenType.EXPRESSION
        assert _values(exprs[0].children[0]) == "a"

    def test_right_operand(self):
        exprs = _parse("a + b")
        assert _type(exprs[0].children[1]) == StageSixTokenType.EXPRESSION
        assert _values(exprs[0].children[1]) == "b"

    def test_chained_operators(self):
        exprs = _parse("a + b + c")
        assert _type(exprs[0]) == StageSixTokenType.BINARY_OP
        # First split at first +: left=a, right=b + c
        assert _type(exprs[0].children[1]) == StageSixTokenType.BINARY_OP

    def test_numeric_operands(self):
        exprs = _parse("1 + 2")
        assert _type(exprs[0].children[0]) == StageSixTokenType.NUMERIC_LITERAL
        assert _type(exprs[0].children[1]) == StageSixTokenType.NUMERIC_LITERAL

    def test_logical_and(self):
        exprs = _parse("a && b")
        assert _type(exprs[0]) == StageSixTokenType.BINARY_OP

    def test_logical_or(self):
        exprs = _parse("a || b")
        assert _type(exprs[0]) == StageSixTokenType.BINARY_OP

    def test_not_equals(self):
        exprs = _parse("a != b")
        assert _type(exprs[0]) == StageSixTokenType.BINARY_OP

    def test_less_than_or_equal(self):
        exprs = _parse("a <= b")
        assert _type(exprs[0]) == StageSixTokenType.BINARY_OP

    def test_modulo(self):
        exprs = _parse("i % 15")
        assert _type(exprs[0]) == StageSixTokenType.BINARY_OP


# ── For Loop ─────────────────────────────────────────────────────────


class TestForLoop:
    def test_basic_for(self):
        exprs = _parse("for x in items\n  process(x)")
        assert _type(exprs[0]) == StageSixTokenType.FOR_LOOP

    def test_variable_child(self):
        exprs = _parse("for x in items\n  body")
        assert _type(exprs[0].children[0]) == StageSixTokenType.EXPRESSION
        assert _values(exprs[0].children[0]) == "x"

    def test_iterable_child(self):
        exprs = _parse("for x in items\n  body")
        assert _type(exprs[0].children[1]) == StageSixTokenType.EXPRESSION
        assert _values(exprs[0].children[1]) == "items"

    def test_iterable_is_function_call(self):
        exprs = _parse("for i in range(10)\n  body")
        assert _type(exprs[0].children[1]) == StageSixTokenType.FUNCTION_CALL

    def test_body_children(self):
        exprs = _parse("for x in items\n  a\n  b")
        # variable + iterable + 2 body children
        assert len(exprs[0].children) == 4

    def test_nested_for(self):
        exprs = _parse("for x in items\n  for y in other\n    body")
        inner_for = exprs[0].children[2]
        assert _type(inner_for) == StageSixTokenType.FOR_LOOP


# ── While Loop ───────────────────────────────────────────────────────


class TestWhileLoop:
    def test_basic_while(self):
        exprs = _parse("while running\n  tick()")
        assert _type(exprs[0]) == StageSixTokenType.WHILE_LOOP

    def test_condition_child(self):
        exprs = _parse("while x > 0\n  body")
        assert _type(exprs[0].children[0]) == StageSixTokenType.BINARY_OP

    def test_simple_condition(self):
        exprs = _parse("while running\n  body")
        assert _type(exprs[0].children[0]) == StageSixTokenType.EXPRESSION

    def test_body_children(self):
        exprs = _parse("while true\n  a\n  b")
        assert len(exprs[0].children) == 3


# ── If / Elif / Else ─────────────────────────────────────────────────


class TestIfExpr:
    def test_basic_if(self):
        exprs = _parse("if x > 0\n  positive")
        assert _type(exprs[0]) == StageSixTokenType.IF_EXPR

    def test_condition_is_binary_op(self):
        exprs = _parse("if x > 0\n  body")
        assert _type(exprs[0].children[0]) == StageSixTokenType.BINARY_OP

    def test_body_child(self):
        exprs = _parse("if true\n  body")
        assert len(exprs[0].children) >= 2


class TestElifExpr:
    def test_basic_elif(self):
        exprs = _parse("if x > 0\n  a\nelif x < 0\n  b")
        assert _type(exprs[1]) == StageSixTokenType.ELIF_EXPR

    def test_elif_condition(self):
        exprs = _parse("if x > 0\n  a\nelif x < 0\n  b")
        assert _type(exprs[1].children[0]) == StageSixTokenType.BINARY_OP


class TestElseExpr:
    def test_basic_else(self):
        exprs = _parse("if x > 0\n  a\nelse\n  b")
        assert _type(exprs[1]) == StageSixTokenType.ELSE_EXPR

    def test_else_has_body(self):
        exprs = _parse("if true\n  a\nelse\n  b")
        assert len(exprs[1].children) >= 1


class TestIfElseChain:
    def test_if_elif_else(self):
        exprs = _parse("if x > 0\n  a\nelif x == 0\n  b\nelse\n  c")
        assert _type(exprs[0]) == StageSixTokenType.IF_EXPR
        assert _type(exprs[1]) == StageSixTokenType.ELIF_EXPR
        assert _type(exprs[2]) == StageSixTokenType.ELSE_EXPR

    def test_nested_if_in_for(self):
        exprs = _parse("for x in items\n  if x > 0\n    process(x)\n  else\n    skip()")
        for_loop = exprs[0]
        body = for_loop.children[2:]
        types = [_type(c) for c in body]
        assert StageSixTokenType.IF_EXPR in types
        assert StageSixTokenType.ELSE_EXPR in types


# ── Match ────────────────────────────────────────────────────────────


class TestMatchExpr:
    def test_basic_match(self):
        exprs = _parse("match x\n  case1\n  case2")
        assert _type(exprs[0]) == StageSixTokenType.MATCH_EXPR

    def test_match_has_children(self):
        exprs = _parse("match x\n  a\n  b")
        assert len(exprs[0].children) >= 2


# ── Expression Fallback ──────────────────────────────────────────────


class TestExpressionFallback:
    def test_single_identifier(self):
        exprs = _parse("x")
        assert _type(exprs[0]) == StageSixTokenType.EXPRESSION

    def test_non_digit_identifier(self):
        exprs = _parse("hello")
        assert _type(exprs[0]) == StageSixTokenType.EXPRESSION

    def test_identifier_not_keyword(self):
        exprs = _parse("myvar")
        assert _type(exprs[0]) == StageSixTokenType.EXPRESSION


# ── Complex Decomposition ────────────────────────────────────────────


class TestComplexDecomposition:
    def test_assignment_of_binary_op(self):
        exprs = _parse("result := a + b")
        assert _type(exprs[0]) == StageSixTokenType.ASSIGNMENT
        assert _type(exprs[0].children[0]) == StageSixTokenType.EXPRESSION
        assert _type(exprs[0].children[1]) == StageSixTokenType.BINARY_OP
        assert _type(exprs[0].children[1].children[0]) == StageSixTokenType.EXPRESSION
        assert _type(exprs[0].children[1].children[1]) == StageSixTokenType.EXPRESSION

    def test_assignment_of_function_call(self):
        exprs = _parse("x := foo(1, 2)")
        assert _type(exprs[0]) == StageSixTokenType.ASSIGNMENT
        call = exprs[0].children[1]
        assert _type(call) == StageSixTokenType.FUNCTION_CALL
        assert len(call.children) == 3

    def test_for_with_function_call_iterable(self):
        exprs = _parse("for i in range(10)\n  body")
        iterable = exprs[0].children[1]
        assert _type(iterable) == StageSixTokenType.FUNCTION_CALL

    def test_if_with_compound_condition(self):
        exprs = _parse("if a > 0 && b < 10\n  body")
        condition = exprs[0].children[0]
        assert _type(condition) == StageSixTokenType.BINARY_OP

    def test_deeply_nested_decomposition(self):
        exprs = _parse("f := (n) =>\n  for i in range(n)\n    if i > 5\n      process(i)")
        func = exprs[0].children[1]
        assert _type(func) == StageSixTokenType.FUNCTION_DEF
        for_loop = func.children[0]
        assert _type(for_loop) == StageSixTokenType.FOR_LOOP
        if_expr = for_loop.children[2]
        assert _type(if_expr) == StageSixTokenType.IF_EXPR
        call = if_expr.children[1]
        assert _type(call) == StageSixTokenType.FUNCTION_CALL

    def test_multiple_assignments(self):
        exprs = _parse("x := 1\ny := 2\nz := 3")
        assert len(exprs) == 3
        assert all(_type(e) == StageSixTokenType.ASSIGNMENT for e in exprs)

    def test_mixed_top_level(self):
        exprs = _parse("x := 1\nfoo()\nif true\n  bar()")
        assert _type(exprs[0]) == StageSixTokenType.ASSIGNMENT
        assert _type(exprs[1]) == StageSixTokenType.FUNCTION_CALL
        assert _type(exprs[2]) == StageSixTokenType.IF_EXPR


# ── Edge Cases ───────────────────────────────────────────────────────


class TestEdgeCases:
    def test_empty_input(self):
        assert _parse("") == []

    def test_only_newlines(self):
        assert _parse("\n\n\n") == []

    def test_nested_function_call_as_arg(self):
        exprs = _parse("foo(bar(baz(1)))")
        assert _type(exprs[0]) == StageSixTokenType.FUNCTION_CALL
        inner = exprs[0].children[1]
        assert _type(inner) == StageSixTokenType.FUNCTION_CALL
        innermost = inner.children[1]
        assert _type(innermost) == StageSixTokenType.FUNCTION_CALL

    def test_function_call_wins_over_binary_op(self):
        # foo( matches function call before + matches binary op.
        exprs = _parse("foo(1) + bar(2)")
        assert _type(exprs[0]) == StageSixTokenType.FUNCTION_CALL

    def test_assignment_value_is_identifier(self):
        exprs = _parse("x := y")
        assert _type(exprs[0].children[1]) == StageSixTokenType.EXPRESSION

    def test_chained_binary_ops_nest_right(self):
        exprs = _parse("a + b * c")
        assert _type(exprs[0]) == StageSixTokenType.BINARY_OP
        right = exprs[0].children[1]
        assert _type(right) == StageSixTokenType.BINARY_OP

    def test_function_call_no_args_callee(self):
        exprs = _parse("foo()")
        assert _values(exprs[0].children[0]) == "foo"

    def test_blank_lines_between_expressions(self):
        exprs = _parse("x := 1\n\n\ny := 2")
        assert len(exprs) == 2
        assert all(_type(e) == StageSixTokenType.ASSIGNMENT for e in exprs)
