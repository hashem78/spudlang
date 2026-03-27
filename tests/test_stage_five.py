# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from typing import Generator

import structlog

from spud.core.position import Position
from spud.di.stage_four_trie import create_stage_four_trie
from spud.di.stage_two_trie import create_stage_two_trie
from spud.stage_five.stage_five import StageFive
from spud.stage_five.stage_five_token import StageFiveToken
from spud.stage_five.stage_five_token_type import StageFiveTokenType
from spud.stage_four.stage_four import StageFour
from spud.stage_one.stage_one import StageOne
from spud.stage_three.stage_three import StageThree
from spud.stage_two.stage_two import StageTwo

INDENT = StageFiveTokenType.INDENT
DEDENT = StageFiveTokenType.DEDENT
NL = StageFiveTokenType.NEW_LINE
ID = StageFiveTokenType.IDENTIFIER


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


def _types(tokens: list[StageFiveToken]) -> list[StageFiveTokenType]:
    return [t.token_type for t in tokens]


def _values(tokens: list[StageFiveToken]) -> list[str]:
    return [t.value for t in tokens if t.value]


# ── Empty Input ─────────────────────────────────────────────────────


class TestEmptyInput:
    def test_empty_string(self):
        assert _parse("") == []

    def test_only_newlines(self):
        assert _parse("\n\n\n") == []

    def test_only_spaces(self):
        assert _parse("   ") == []


# ── Flat Expressions ────────────────────────────────────────────────


class TestFlatExpressions:
    def test_single_line(self):
        tokens = _parse("x := 1")
        types = _types(tokens)
        assert INDENT not in types
        assert DEDENT not in types
        assert types[-1] == NL

    def test_single_line_values(self):
        tokens = _parse("x := 1")
        assert _values(tokens) == ["x", ":=", "1"]

    def test_two_lines(self):
        tokens = _parse("x := 1\ny := 2")
        types = _types(tokens)
        assert INDENT not in types
        assert DEDENT not in types
        assert types.count(NL) == 2

    def test_two_lines_values(self):
        tokens = _parse("x := 1\ny := 2")
        assert _values(tokens) == ["x", ":=", "1", "y", ":=", "2"]

    def test_three_lines(self):
        tokens = _parse("a := 1\nb := 2\nc := 3")
        types = _types(tokens)
        assert INDENT not in types
        assert DEDENT not in types
        assert types.count(NL) == 3

    def test_blank_lines_between(self):
        tokens = _parse("a := 1\n\n\nb := 2")
        assert _values(tokens) == ["a", ":=", "1", "b", ":=", "2"]

    def test_trailing_newlines(self):
        tokens = _parse("x := 1\n\n\n")
        assert _values(tokens) == ["x", ":=", "1"]


# ── Single Level Nesting ───────────────────────────────────────────


class TestSingleLevelNesting:
    def test_one_child(self):
        tokens = _parse("parent\n  child")
        types = _types(tokens)
        assert types == [ID, NL, INDENT, ID, NL, DEDENT]

    def test_two_children(self):
        tokens = _parse("parent\n  child1\n  child2")
        types = _types(tokens)
        assert types == [ID, NL, INDENT, ID, NL, ID, NL, DEDENT]

    def test_parent_after_nested(self):
        tokens = _parse("a\n  b\nc")
        types = _types(tokens)
        assert types == [ID, NL, INDENT, ID, NL, DEDENT, ID, NL]


# ── Multi Level Nesting ────────────────────────────────────────────


class TestMultiLevelNesting:
    def test_two_levels(self):
        tokens = _parse("a\n  b\n    c")
        types = _types(tokens)
        assert types == [ID, NL, INDENT, ID, NL, INDENT, ID, NL, DEDENT, DEDENT]

    def test_three_levels(self):
        tokens = _parse("a\n  b\n    c\n      d")
        types = _types(tokens)
        assert types == [ID, NL, INDENT, ID, NL, INDENT, ID, NL, INDENT, ID, NL, DEDENT, DEDENT, DEDENT]

    def test_deep_then_return_to_root(self):
        tokens = _parse("a\n  b\n    c\nd")
        types = _types(tokens)
        assert types == [ID, NL, INDENT, ID, NL, INDENT, ID, NL, DEDENT, DEDENT, ID, NL]

    def test_deep_then_return_to_middle(self):
        tokens = _parse("a\n  b\n    c\n  d")
        types = _types(tokens)
        assert types == [ID, NL, INDENT, ID, NL, INDENT, ID, NL, DEDENT, ID, NL, DEDENT]


# ── Sibling Blocks ─────────────────────────────────────────────────


class TestSiblingBlocks:
    def test_two_parents_with_children(self):
        tokens = _parse("a\n  a1\n  a2\nb\n  b1\n  b2")
        types = _types(tokens)
        assert types == [
            ID,
            NL,
            INDENT,
            ID,
            NL,
            ID,
            NL,
            DEDENT,
            ID,
            NL,
            INDENT,
            ID,
            NL,
            ID,
            NL,
            DEDENT,
        ]

    def test_alternating_flat_and_nested(self):
        tokens = _parse("a\nb\n  b1\nc\nd\n  d1")
        types = _types(tokens)
        assert types == [
            ID,
            NL,
            ID,
            NL,
            INDENT,
            ID,
            NL,
            DEDENT,
            ID,
            NL,
            ID,
            NL,
            INDENT,
            ID,
            NL,
            DEDENT,
        ]


# ── If/Else Pattern ────────────────────────────────────────────────


class TestIfElsePattern:
    def test_if_with_body(self):
        tokens = _parse('if x > 0\n  "positive"')
        types = _types(tokens)
        assert INDENT in types
        assert DEDENT in types

    def test_if_else_with_bodies(self):
        tokens = _parse('if x > 0\n  "positive"\nelse\n  "negative"')
        types = _types(tokens)
        # Two INDENT/DEDENT pairs — one for each block.
        assert types.count(INDENT) == 2
        assert types.count(DEDENT) == 2


# ── Function Pattern ───────────────────────────────────────────────


class TestFunctionPattern:
    def test_function_with_body(self):
        tokens = _parse("add := (a, b) =>\n  result := a + b\n  result")
        types = _types(tokens)
        assert types.count(INDENT) == 1
        assert types.count(DEDENT) == 1

    def test_function_then_flat(self):
        tokens = _parse("f := (x) =>\n  x + 1\ny := f(5)")
        types = _types(tokens)
        assert types.count(INDENT) == 1
        assert types.count(DEDENT) == 1

    def test_nested_function_calls(self):
        tokens = _parse("outer := (n) =>\n  for i in range(n)\n    if i > 0\n      process(i)")
        types = _types(tokens)
        assert types.count(INDENT) == 3
        assert types.count(DEDENT) == 3


# ── Position Tracking ──────────────────────────────────────────────


class TestPositionTracking:
    def test_first_token_position(self):
        tokens = _parse("x := 1")
        assert tokens[0].position == Position(line=0, column=0)

    def test_second_line_position(self):
        tokens = _parse("x := 1\ny := 2")
        # Find first token of second line (after NL).
        y_token = [t for t in tokens if t.value == "y"][0]
        assert y_token.position == Position(line=1, column=0)

    def test_child_position(self):
        tokens = _parse("parent\n  child")
        child_token = [t for t in tokens if t.value == "child"][0]
        assert child_token.position == Position(line=1, column=2)

    def test_indent_position(self):
        tokens = _parse("parent\n  child")
        indent = [t for t in tokens if t.token_type == INDENT][0]
        assert indent.position == Position(line=1, column=2)


# ── Token Preservation ─────────────────────────────────────────────


class TestTokenPreservation:
    def test_keywords_preserved(self):
        tokens = _parse("for x in items")
        types = _types(tokens)
        assert StageFiveTokenType.FOR in types
        assert StageFiveTokenType.IN in types

    def test_string_preserved(self):
        tokens = _parse('"hello world"')
        types = _types(tokens)
        assert StageFiveTokenType.STRING in types

    def test_operators_preserved(self):
        tokens = _parse("a == b && c != d")
        types = _types(tokens)
        assert StageFiveTokenType.EQUALS in types
        assert StageFiveTokenType.LOGICAL_AND in types
        assert StageFiveTokenType.NOT_EQUALS in types

    def test_walrus_preserved(self):
        tokens = _parse("x := 1")
        types = _types(tokens)
        assert StageFiveTokenType.WALRUS in types


# ── Indent Variations ──────────────────────────────────────────────


class TestIndentVariations:
    def test_two_space_indent(self):
        tokens = _parse("a\n  b")
        assert _types(tokens).count(INDENT) == 1

    def test_four_space_indent(self):
        tokens = _parse("a\n    b")
        assert _types(tokens).count(INDENT) == 1

    def test_mixed_indent_depths(self):
        tokens = _parse("a\n  b\n      c")
        assert _types(tokens).count(INDENT) == 2
        assert _types(tokens).count(DEDENT) == 2

    def test_uneven_siblings(self):
        tokens = _parse("a\n  b\n  c\n    d\n  e")
        types = _types(tokens)
        # a NL INDENT b NL c NL INDENT d NL DEDENT e NL DEDENT
        assert types == [ID, NL, INDENT, ID, NL, ID, NL, INDENT, ID, NL, DEDENT, ID, NL, DEDENT]


# ── Edge Cases ──────────────────────────────────────────────────────


class TestEdgeCases:
    def test_single_token(self):
        tokens = _parse("x")
        assert _types(tokens) == [ID, NL]

    def test_single_string(self):
        tokens = _parse('"hello"')
        types = _types(tokens)
        assert StageFiveTokenType.STRING in types

    def test_many_flat_lines(self):
        lines = "\n".join(f"x{i} := {i}" for i in range(20))
        tokens = _parse(lines)
        types = _types(tokens)
        assert INDENT not in types
        assert DEDENT not in types

    def test_deeply_nested(self):
        text = "a\n  b\n    c\n      d\n        e\n          f"
        tokens = _parse(text)
        types = _types(tokens)
        assert types.count(INDENT) == 5
        assert types.count(DEDENT) == 5

    def test_blank_lines_in_nested_block(self):
        tokens = _parse("a\n  b\n\n  c")
        types = _types(tokens)
        assert types.count(INDENT) == 1
        assert types.count(DEDENT) == 1
        assert _values(tokens) == ["a", "b", "c"]

    def test_indent_dedent_balance(self):
        tokens = _parse("a\n  b\n    c\n      d\ne\n  f")
        types = _types(tokens)
        assert types.count(INDENT) == types.count(DEDENT)

    def test_child_returns_to_exact_parent_indent(self):
        tokens = _parse("a\n  b\n    c\n  d\n    e")
        types = _types(tokens)
        # a NL INDENT b NL INDENT c NL DEDENT d NL INDENT e NL DEDENT DEDENT
        assert types == [ID, NL, INDENT, ID, NL, INDENT, ID, NL, DEDENT, ID, NL, INDENT, ID, NL, DEDENT, DEDENT]
