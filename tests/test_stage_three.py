# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from typing import Generator

import structlog

from spud.di.stage_two_trie import create_stage_two_trie
from spud.stage_one.stage_one import StageOne
from spud.stage_three.stage_three import StageThree
from spud.stage_three.stage_three_token import StageThreeToken
from spud.stage_three.stage_three_token_type import StageThreeTokenType
from spud.stage_two.stage_two import StageTwo


class _StringReader:
    def __init__(self, text: str):
        self._text = text

    def read(self) -> Generator[str, None, None]:
        for char in self._text:
            yield char


def _parse(text: str) -> list[StageThreeToken]:
    reader = _StringReader(text)
    stage_one = StageOne(reader)
    stage_two = StageTwo(stage_one, create_stage_two_trie(), structlog.get_logger())
    stage_three = StageThree(stage_two, structlog.get_logger())
    return list(stage_three.parse())


def _types(tokens: list[StageThreeToken]) -> list[StageThreeTokenType]:
    return [t.token_type for t in tokens]


def _values(tokens: list[StageThreeToken]) -> list[str]:
    return [t.value for t in tokens]


class TestNumericTokens:
    def test_single_digit_produces_numeric(self):
        tokens = _parse("0")
        assert _types(tokens) == [StageThreeTokenType.INT]

    def test_single_digit_zero(self):
        tokens = _parse("0")
        assert tokens[0].token_type == StageThreeTokenType.INT
        assert tokens[0].value == "0"

    def test_single_digit_nine(self):
        tokens = _parse("9")
        assert tokens[0].token_type == StageThreeTokenType.INT
        assert tokens[0].value == "9"

    def test_multi_digit_produces_numeric(self):
        tokens = _parse("42")
        assert _types(tokens) == [StageThreeTokenType.INT]
        assert tokens[0].value == "42"

    def test_large_number_produces_numeric(self):
        tokens = _parse("1234567890")
        assert tokens[0].token_type == StageThreeTokenType.INT
        assert tokens[0].value == "1234567890"

    def test_all_digits_zero_through_nine(self):
        tokens = _parse("1234567890")
        assert tokens[0].token_type == StageThreeTokenType.INT

    def test_numeric_value_preserved(self):
        tokens = _parse("999")
        assert tokens[0].value == "999"

    def test_numeric_not_identifier(self):
        tokens = _parse("42")
        assert tokens[0].token_type != StageThreeTokenType.IDENTIFIER

    def test_two_numbers_separated_by_space(self):
        tokens = _parse("1 2")
        types = _types(tokens)
        assert types == [StageThreeTokenType.INT, StageThreeTokenType.INT]

    def test_two_numbers_values(self):
        tokens = _parse("10 20")
        assert tokens[0].value == "10"
        assert tokens[1].value == "20"


class TestIdentifierTokens:
    def test_pure_alpha_produces_identifier(self):
        tokens = _parse("foo")
        assert tokens[0].token_type == StageThreeTokenType.IDENTIFIER

    def test_mixed_alpha_digit_produces_identifier(self):
        tokens = _parse("x1")
        assert tokens[0].token_type == StageThreeTokenType.IDENTIFIER

    def test_mixed_digit_alpha_produces_identifier(self):
        tokens = _parse("1x")
        assert tokens[0].token_type == StageThreeTokenType.IDENTIFIER

    def test_mixed_alpha_digit_value_preserved(self):
        tokens = _parse("foo42")
        assert tokens[0].token_type == StageThreeTokenType.IDENTIFIER
        assert tokens[0].value == "foo42"

    def test_digit_surrounded_by_alpha_produces_identifier(self):
        tokens = _parse("a1b")
        assert tokens[0].token_type == StageThreeTokenType.IDENTIFIER
        assert tokens[0].value == "a1b"

    def test_underscore_prefix_produces_identifier(self):
        tokens = _parse("_x")
        assert tokens[0].token_type == StageThreeTokenType.IDENTIFIER

    def test_single_alpha_char_produces_identifier(self):
        tokens = _parse("x")
        assert tokens[0].token_type == StageThreeTokenType.IDENTIFIER


class TestNumericAndIdentifierMixed:
    def test_number_then_identifier(self):
        tokens = _parse("42 foo")
        assert tokens[0].token_type == StageThreeTokenType.INT
        assert tokens[1].token_type == StageThreeTokenType.IDENTIFIER

    def test_identifier_then_number(self):
        tokens = _parse("foo 42")
        assert tokens[0].token_type == StageThreeTokenType.IDENTIFIER
        assert tokens[1].token_type == StageThreeTokenType.INT

    def test_binding_with_numeric_rhs(self):
        tokens = _parse("x := 1")
        numeric_tokens = [t for t in tokens if t.token_type == StageThreeTokenType.INT]
        assert len(numeric_tokens) == 1
        assert numeric_tokens[0].value == "1"

    def test_identifier_lhs_not_numeric(self):
        tokens = _parse("x := 1")
        id_tokens = [t for t in tokens if t.token_type == StageThreeTokenType.IDENTIFIER]
        assert len(id_tokens) == 1
        assert id_tokens[0].value == "x"
