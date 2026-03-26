# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from typing import Generator

import structlog

from spud.core.file_reader import FileReader
from spud.core.position import Position
from spud.di.stage_four_trie import create_stage_four_trie
from spud.di.stage_two_trie import create_stage_two_trie
from spud.stage_five.stage_five import StageFive
from spud.stage_five.stage_five_token import StageFiveToken
from spud.stage_five.stage_five_token_type import StageFiveTokenType
from spud.stage_four.stage_four import StageFour
from spud.stage_four.stage_four_token_type import StageFourTokenType
from spud.stage_one.stage_one import StageOne
from spud.stage_three.stage_three import StageThree
from spud.stage_two.stage_two import StageTwo


class _StringReader:
    def __init__(self, text: str):
        self._text = text

    def read(self) -> Generator[str, None, None]:
        for char in self._text:
            yield char


def _parse(text: str) -> list[StageFiveToken]:
    reader = _StringReader(text)
    stage_one = StageOne(reader)
    stage_two = StageTwo(stage_one, create_stage_two_trie(), structlog.get_logger())
    stage_three = StageThree(stage_two, structlog.get_logger())
    stage_four = StageFour(stage_three, create_stage_four_trie(), structlog.get_logger())
    stage_five = StageFive(stage_four, structlog.get_logger())
    return list(stage_five.parse())


def _token_values(expr: StageFiveToken) -> str:
    return " ".join(t.value for t in expr.tokens)


class TestEmptyInput:
    def test_empty_string(self):
        assert _parse("") == []

    def test_only_newlines(self):
        assert _parse("\n\n\n") == []

    def test_only_spaces(self):
        exprs = _parse("   ")
        assert len(exprs) == 0 or all(len(e.tokens) == 0 for e in exprs)


class TestFlatExpressions:
    def test_single_line(self):
        exprs = _parse("x := 1")
        assert len(exprs) == 1
        assert exprs[0].token_type == StageFiveTokenType.EXPRESSION
        assert exprs[0].children == []

    def test_single_line_with_newline(self):
        exprs = _parse("x := 1\n")
        assert len(exprs) == 1
        assert exprs[0].children == []

    def test_two_lines(self):
        exprs = _parse("x := 1\ny := 2")
        assert len(exprs) == 2
        assert _token_values(exprs[0]) == "x := 1"
        assert _token_values(exprs[1]) == "y := 2"

    def test_three_lines(self):
        exprs = _parse("a := 1\nb := 2\nc := 3")
        assert len(exprs) == 3
        assert all(e.children == [] for e in exprs)

    def test_blank_lines_between(self):
        exprs = _parse("a := 1\n\n\nb := 2")
        assert len(exprs) == 2
        assert _token_values(exprs[0]) == "a := 1"
        assert _token_values(exprs[1]) == "b := 2"

    def test_trailing_newlines(self):
        exprs = _parse("x := 1\n\n\n")
        assert len(exprs) == 1


class TestSingleLevelNesting:
    def test_one_child(self):
        exprs = _parse("parent\n  child")
        assert len(exprs) == 1
        assert len(exprs[0].children) == 1
        assert _token_values(exprs[0].children[0]) == "child"

    def test_two_children(self):
        exprs = _parse("parent\n  child1\n  child2")
        assert len(exprs) == 1
        assert len(exprs[0].children) == 2
        assert _token_values(exprs[0].children[0]) == "child1"
        assert _token_values(exprs[0].children[1]) == "child2"

    def test_child_has_no_children(self):
        exprs = _parse("parent\n  child")
        assert exprs[0].children[0].children == []

    def test_parent_after_nested(self):
        exprs = _parse("a\n  b\nc")
        assert len(exprs) == 2
        assert _token_values(exprs[0]) == "a"
        assert len(exprs[0].children) == 1
        assert _token_values(exprs[1]) == "c"
        assert exprs[1].children == []


class TestMultiLevelNesting:
    def test_two_levels(self):
        exprs = _parse("a\n  b\n    c")
        assert len(exprs) == 1
        assert len(exprs[0].children) == 1
        assert len(exprs[0].children[0].children) == 1
        assert _token_values(exprs[0].children[0].children[0]) == "c"

    def test_three_levels(self):
        exprs = _parse("a\n  b\n    c\n      d")
        assert len(exprs) == 1
        child = exprs[0].children[0].children[0].children[0]
        assert _token_values(child) == "d"
        assert child.children == []

    def test_deep_then_return_to_root(self):
        exprs = _parse("a\n  b\n    c\nd")
        assert len(exprs) == 2
        assert _token_values(exprs[0]) == "a"
        assert len(exprs[0].children) == 1
        assert len(exprs[0].children[0].children) == 1
        assert _token_values(exprs[1]) == "d"
        assert exprs[1].children == []

    def test_deep_then_return_to_middle(self):
        exprs = _parse("a\n  b\n    c\n  d")
        assert len(exprs) == 1
        assert len(exprs[0].children) == 2
        assert _token_values(exprs[0].children[0]) == "b"
        assert len(exprs[0].children[0].children) == 1
        assert _token_values(exprs[0].children[1]) == "d"
        assert exprs[0].children[1].children == []


class TestSiblingBlocks:
    def test_two_parents_with_children(self):
        exprs = _parse("a\n  a1\n  a2\nb\n  b1\n  b2")
        assert len(exprs) == 2
        assert len(exprs[0].children) == 2
        assert len(exprs[1].children) == 2
        assert _token_values(exprs[0].children[0]) == "a1"
        assert _token_values(exprs[1].children[1]) == "b2"

    def test_alternating_flat_and_nested(self):
        exprs = _parse("a\nb\n  b1\nc\nd\n  d1")
        assert len(exprs) == 4
        assert exprs[0].children == []
        assert len(exprs[1].children) == 1
        assert exprs[2].children == []
        assert len(exprs[3].children) == 1


class TestIfElsePattern:
    def test_if_with_body(self):
        exprs = _parse("if x > 0\n  \"positive\"")
        assert len(exprs) == 1
        assert len(exprs[0].children) == 1

    def test_if_else_with_bodies(self):
        exprs = _parse("if x > 0\n  \"positive\"\nelse\n  \"negative\"")
        assert len(exprs) == 2
        assert len(exprs[0].children) == 1
        assert len(exprs[1].children) == 1

    def test_nested_if_else(self):
        exprs = _parse("for i in items\n  if i > 5\n    \"big\"\n  else\n    \"small\"")
        assert len(exprs) == 1
        for_expr = exprs[0]
        assert len(for_expr.children) == 2
        assert len(for_expr.children[0].children) == 1
        assert len(for_expr.children[1].children) == 1


class TestFunctionPattern:
    def test_function_with_body(self):
        exprs = _parse("add := (a, b) =>\n  result := a + b\n  result")
        assert len(exprs) == 1
        assert len(exprs[0].children) == 2

    def test_function_then_flat(self):
        exprs = _parse("f := (x) =>\n  x + 1\ny := f(5)")
        assert len(exprs) == 2
        assert len(exprs[0].children) == 1
        assert exprs[1].children == []

    def test_nested_function_calls(self):
        exprs = _parse("outer := (n) =>\n  for i in range(n)\n    if i > 0\n      process(i)")
        assert len(exprs) == 1
        assert len(exprs[0].children) == 1
        assert len(exprs[0].children[0].children) == 1
        assert len(exprs[0].children[0].children[0].children) == 1


class TestPositionTracking:
    def test_first_line_position(self):
        exprs = _parse("x := 1")
        assert exprs[0].position == Position(line=1, column=0)

    def test_second_line_position(self):
        exprs = _parse("x := 1\ny := 2")
        assert exprs[1].position == Position(line=2, column=0)

    def test_child_position(self):
        exprs = _parse("parent\n  child")
        assert exprs[0].children[0].position == Position(line=2, column=2)

    def test_deep_child_position(self):
        exprs = _parse("a\n  b\n    c")
        assert exprs[0].children[0].children[0].position == Position(line=3, column=4)


class TestTokenPreservation:
    def test_tokens_preserved(self):
        exprs = _parse("x := 1 + 2")
        types = [t.token_type for t in exprs[0].tokens]
        assert StageFourTokenType.IDENTIFIER in types
        assert StageFourTokenType.WALRUS in types
        assert StageFourTokenType.PLUS in types

    def test_keywords_preserved(self):
        exprs = _parse("for x in items")
        types = [t.token_type for t in exprs[0].tokens]
        assert StageFourTokenType.FOR in types
        assert StageFourTokenType.IN in types

    def test_string_preserved(self):
        exprs = _parse('"hello world"')
        types = [t.token_type for t in exprs[0].tokens]
        assert StageFourTokenType.STRING in types

    def test_operators_preserved(self):
        exprs = _parse("a == b && c != d")
        types = [t.token_type for t in exprs[0].tokens]
        assert StageFourTokenType.EQUALS in types
        assert StageFourTokenType.LOGICAL_AND in types
        assert StageFourTokenType.NOT_EQUALS in types


class TestIndentVariations:
    def test_two_space_indent(self):
        exprs = _parse("a\n  b")
        assert len(exprs[0].children) == 1

    def test_four_space_indent(self):
        exprs = _parse("a\n    b")
        assert len(exprs[0].children) == 1

    def test_mixed_indent_depths(self):
        exprs = _parse("a\n  b\n      c")
        assert len(exprs) == 1
        assert len(exprs[0].children) == 1
        assert len(exprs[0].children[0].children) == 1

    def test_uneven_siblings(self):
        exprs = _parse("a\n  b\n  c\n    d\n  e")
        assert len(exprs) == 1
        assert len(exprs[0].children) == 3
        assert exprs[0].children[0].children == []
        assert len(exprs[0].children[1].children) == 1
        assert exprs[0].children[2].children == []


class TestEdgeCases:
    def test_single_token_expression(self):
        exprs = _parse("x")
        assert len(exprs) == 1
        assert len(exprs[0].tokens) == 1

    def test_single_string(self):
        exprs = _parse('"hello"')
        assert len(exprs) == 1

    def test_many_flat_lines(self):
        lines = "\n".join(f"x{i} := {i}" for i in range(20))
        exprs = _parse(lines)
        assert len(exprs) == 20
        assert all(e.children == [] for e in exprs)

    def test_deeply_nested(self):
        text = "a\n  b\n    c\n      d\n        e\n          f"
        exprs = _parse(text)
        assert len(exprs) == 1
        node = exprs[0]
        for _ in range(5):
            assert len(node.children) == 1
            node = node.children[0]
        assert node.children == []

    def test_blank_lines_in_nested_block(self):
        exprs = _parse("a\n  b\n\n  c")
        assert len(exprs) == 1
        assert len(exprs[0].children) == 2

    def test_only_indented_lines(self):
        exprs = _parse("  a\n  b")
        assert len(exprs) == 2

    def test_child_returns_to_exact_parent_indent(self):
        exprs = _parse("a\n  b\n    c\n  d\n    e")
        assert len(exprs) == 1
        assert len(exprs[0].children) == 2
        assert len(exprs[0].children[0].children) == 1
        assert len(exprs[0].children[1].children) == 1
