# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from typing import Generator

from spud.core.position import Position
from spud.di.stage_two_trie import create_stage_two_trie
from spud.stage_one.stage_one import StageOne
from spud.stage_two.keyword_pass import KeywordPass
from spud.stage_two.stage_two_token import DefinedStageTwoToken, StageTwoToken
from spud.stage_two.stage_two_token_type import StageTwoTokenType
from spud.stage_two.string_pass import StringPass


class _StringReader:
    def __init__(self, text: str):
        self._text = text

    def read(self) -> Generator[str, None, None]:
        for char in self._text:
            yield char


def _parse(text: str) -> list[StageTwoToken]:
    reader = _StringReader(text)
    stage_one = StageOne(reader)
    string_pass = StringPass(stage_one)
    trie = create_stage_two_trie()
    keyword_pass = KeywordPass(string_pass, trie)
    return list(keyword_pass.parse())


def _types(tokens: list[StageTwoToken]) -> list[StageTwoTokenType]:
    return [t.token_type for t in tokens]


class TestResolvePendingWithBoundary:
    def test_keyword_followed_by_space(self):
        tokens = _parse("for ")
        assert tokens[0].token_type == StageTwoTokenType.FOR

    def test_keyword_followed_by_newline(self):
        tokens = _parse("for\n")
        assert tokens[0].token_type == StageTwoTokenType.FOR

    def test_keyword_at_end_of_input(self):
        tokens = _parse("for")
        assert _types(tokens) == [StageTwoTokenType.FOR]

    def test_keyword_between_spaces(self):
        tokens = _parse(" for ")
        assert StageTwoTokenType.FOR in _types(tokens)


class TestResolvePendingWithIdentifier:
    def test_keyword_followed_by_letter(self):
        tokens = _parse("forl")
        assert StageTwoTokenType.FOR not in _types(tokens)
        assert all(isinstance(t, DefinedStageTwoToken) for t in tokens)
        assert len(tokens) == 4

    def test_keyword_followed_by_digit(self):
        tokens = _parse("for1")
        assert StageTwoTokenType.FOR not in _types(tokens)

    def test_keyword_followed_by_underscore(self):
        tokens = _parse("for_")
        assert StageTwoTokenType.FOR not in _types(tokens)


class TestCompleteMatchAfterBoundary:
    def test_keyword_at_start(self):
        tokens = _parse("for")
        assert _types(tokens) == [StageTwoTokenType.FOR]

    def test_keyword_after_space(self):
        tokens = _parse(" for")
        assert tokens[-1].token_type == StageTwoTokenType.FOR

    def test_keyword_after_newline(self):
        tokens = _parse("\nfor")
        assert _types(tokens) == [StageTwoTokenType.NEW_LINE, StageTwoTokenType.FOR]

    def test_multiple_keywords(self):
        tokens = _parse("for in while")
        types = _types(tokens)
        assert types == [
            StageTwoTokenType.FOR,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.IN,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.WHILE,
        ]


class TestCompleteMatchAfterIdentifier:
    def test_keyword_preceded_by_letter(self):
        tokens = _parse("lfor")
        assert StageTwoTokenType.FOR not in _types(tokens)
        assert all(len(t.token_type.value) == 1 for t in tokens)

    def test_keyword_surrounded_by_letters(self):
        tokens = _parse("lforl")
        assert StageTwoTokenType.FOR not in _types(tokens)

    def test_keyword_inside_identifier(self):
        tokens = _parse("xfalsey")
        assert StageTwoTokenType.FALSE not in _types(tokens)


class TestNoMatch:
    def test_single_char(self):
        tokens = _parse("x")
        assert _types(tokens) == [StageTwoTokenType.X_LOWERCASE]

    def test_non_keyword_word(self):
        tokens = _parse("hello")
        assert len(tokens) == 5
        assert all(len(t.token_type.value) == 1 for t in tokens)

    def test_boundary_token_pass_through(self):
        tokens = _parse(" ")
        assert _types(tokens) == [StageTwoTokenType.SPACE]

    def test_newline_pass_through(self):
        tokens = _parse("\n")
        assert _types(tokens) == [StageTwoTokenType.NEW_LINE]

    def test_incomplete_keyword(self):
        tokens = _parse("fals")
        assert StageTwoTokenType.FALSE not in _types(tokens)
        assert all(len(t.token_type.value) == 1 for t in tokens)


class TestStringLiteralFlushesState:
    def test_pending_keyword_then_string(self):
        tokens = _parse('for "hello"')
        types = _types(tokens)
        assert types == [
            StageTwoTokenType.FOR,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.STRING,
        ]

    def test_partial_trie_then_string(self):
        tokens = _parse('fa"hello"')
        types = _types(tokens)
        assert types[0] == StageTwoTokenType.F_LOWERCASE
        assert types[1] == StageTwoTokenType.A_LOWERCASE
        assert StageTwoTokenType.STRING in types

    def test_string_resets_to_after_boundary(self):
        tokens = _parse('"hello"for')
        types = _types(tokens)
        assert types[0] == StageTwoTokenType.STRING
        assert StageTwoTokenType.FOR in types

    def test_string_between_keywords(self):
        tokens = _parse('for "x" if')
        types = _types(tokens)
        assert types == [
            StageTwoTokenType.FOR,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.STRING,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.IF,
        ]


class TestBackToBackKeywords:
    def test_adjacent_same_keyword(self):
        tokens = _parse("forfor")
        assert StageTwoTokenType.FOR not in _types(tokens)
        assert all(len(t.token_type.value) == 1 for t in tokens)

    def test_adjacent_different_keywords(self):
        tokens = _parse("forif")
        assert StageTwoTokenType.FOR not in _types(tokens)
        assert StageTwoTokenType.IF not in _types(tokens)


class TestPositionTracking:
    def test_keyword_position(self):
        tokens = _parse("for")
        assert tokens[0].position == Position(line=0, column=0)

    def test_keyword_after_space_position(self):
        tokens = _parse(" for")
        for_token = next(t for t in tokens if t.token_type == StageTwoTokenType.FOR)
        assert for_token.position == Position(line=0, column=1)

    def test_rejected_keyword_preserves_char_positions(self):
        tokens = _parse("forl")
        assert tokens[0].position == Position(line=0, column=0)
        assert tokens[1].position == Position(line=0, column=1)
        assert tokens[2].position == Position(line=0, column=2)
        assert tokens[3].position == Position(line=0, column=3)
