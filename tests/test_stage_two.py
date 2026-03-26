# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from typing import Generator

import structlog

from spud.core.position import Position
from spud.di.stage_two_trie import create_stage_two_trie
from spud.stage_one.stage_one import StageOne
from spud.stage_two.stage_two import StageTwo
from spud.stage_two.stage_two_token import StageTwoToken, StringLiteralStageTwoToken
from spud.stage_two.stage_two_token_type import StageTwoTokenType


class _StringReader:
    def __init__(self, text: str):
        self._text = text

    def read(self) -> Generator[str, None, None]:
        for char in self._text:
            yield char


def _parse(text: str) -> list[StageTwoToken]:
    reader = _StringReader(text)
    stage_one = StageOne(reader)
    trie = create_stage_two_trie()
    logger = structlog.get_logger()
    stage_two = StageTwo(stage_one, trie, logger)
    return list(stage_two.parse())


def _types(tokens: list[StageTwoToken]) -> list[StageTwoTokenType]:
    return [t.token_type for t in tokens]


class TestKeywordMatchesAtBoundaries:
    def test_keyword_alone(self):
        tokens = _parse("for")
        assert _types(tokens) == [StageTwoTokenType.FOR]

    def test_keyword_with_spaces(self):
        tokens = _parse(" for ")
        types = _types(tokens)
        assert StageTwoTokenType.FOR in types

    def test_keyword_between_words(self):
        tokens = _parse("a for b")
        types = _types(tokens)
        assert types == [
            StageTwoTokenType.A_LOWERCASE,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.FOR,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.B_LOWERCASE,
        ]

    def test_keyword_at_start_followed_by_space(self):
        tokens = _parse("for ")
        assert tokens[0].token_type == StageTwoTokenType.FOR

    def test_keyword_at_end_preceded_by_space(self):
        tokens = _parse(" for")
        assert tokens[-1].token_type == StageTwoTokenType.FOR

    def test_keyword_followed_by_newline(self):
        tokens = _parse("for\n")
        assert tokens[0].token_type == StageTwoTokenType.FOR

    def test_keyword_preceded_by_newline(self):
        tokens = _parse("\nfor")
        types = _types(tokens)
        assert types == [StageTwoTokenType.NEW_LINE, StageTwoTokenType.FOR]

    def test_keyword_between_newlines(self):
        tokens = _parse("\nfor\n")
        types = _types(tokens)
        assert types == [
            StageTwoTokenType.NEW_LINE,
            StageTwoTokenType.FOR,
            StageTwoTokenType.NEW_LINE,
        ]


class TestKeywordRejectedInsideIdentifiers:
    def test_keyword_prefix(self):
        tokens = _parse("lfor")
        types = _types(tokens)
        assert StageTwoTokenType.FOR not in types
        assert all(len(t.token_type.value) == 1 for t in tokens)

    def test_keyword_suffix(self):
        tokens = _parse("forl")
        types = _types(tokens)
        assert StageTwoTokenType.FOR not in types

    def test_keyword_infix(self):
        tokens = _parse("lforl")
        types = _types(tokens)
        assert StageTwoTokenType.FOR not in types

    def test_false_prefix(self):
        tokens = _parse("xfalse")
        types = _types(tokens)
        assert StageTwoTokenType.FALSE not in types

    def test_false_suffix(self):
        tokens = _parse("falsey")
        types = _types(tokens)
        assert StageTwoTokenType.FALSE not in types

    def test_false_infix(self):
        tokens = _parse("xfalsey")
        types = _types(tokens)
        assert StageTwoTokenType.FALSE not in types

    def test_if_prefix(self):
        tokens = _parse("xif")
        types = _types(tokens)
        assert StageTwoTokenType.IF not in types

    def test_if_suffix(self):
        tokens = _parse("ify")
        types = _types(tokens)
        assert StageTwoTokenType.IF not in types

    def test_or_inside_word(self):
        tokens = _parse("ford")
        types = _types(tokens)
        assert StageTwoTokenType.OR not in types
        assert StageTwoTokenType.FOR not in types

    def test_in_inside_word(self):
        tokens = _parse("line")
        types = _types(tokens)
        assert StageTwoTokenType.IN not in types


class TestAllKeywords:
    def test_false(self):
        assert _types(_parse("false")) == [StageTwoTokenType.FALSE]

    def test_true(self):
        assert _types(_parse("true")) == [StageTwoTokenType.TRUE]

    def test_if(self):
        assert _types(_parse("if")) == [StageTwoTokenType.IF]

    def test_for(self):
        assert _types(_parse("for")) == [StageTwoTokenType.FOR]

    def test_while(self):
        assert _types(_parse("while")) == [StageTwoTokenType.WHILE]

    def test_or(self):
        assert _types(_parse("or")) == [StageTwoTokenType.OR]

    def test_and(self):
        assert _types(_parse("and")) == [StageTwoTokenType.AND]

    def test_in(self):
        assert _types(_parse("in")) == [StageTwoTokenType.IN]


class TestPassThroughTokens:
    def test_single_char(self):
        tokens = _parse("x")
        assert _types(tokens) == [StageTwoTokenType.X_LOWERCASE]

    def test_space(self):
        tokens = _parse(" ")
        assert _types(tokens) == [StageTwoTokenType.SPACE]

    def test_newline(self):
        tokens = _parse("\n")
        assert _types(tokens) == [StageTwoTokenType.NEW_LINE]

    def test_symbols(self):
        tokens = _parse("+-")
        assert _types(tokens) == [StageTwoTokenType.PLUS, StageTwoTokenType.HYPHEN]

    def test_non_keyword_word(self):
        tokens = _parse("hello")
        types = _types(tokens)
        assert types == [
            StageTwoTokenType.H_LOWERCASE,
            StageTwoTokenType.E_LOWERCASE,
            StageTwoTokenType.L_LOWERCASE,
            StageTwoTokenType.L_LOWERCASE,
            StageTwoTokenType.O_LOWERCASE,
        ]


class TestSharedPrefixKeywords:
    def test_for_and_false_share_f(self):
        tokens = _parse("for false")
        types = _types(tokens)
        assert StageTwoTokenType.FOR in types
        assert StageTwoTokenType.FALSE in types

    def test_if_and_in_share_i(self):
        tokens = _parse("if in")
        types = _types(tokens)
        assert StageTwoTokenType.IF in types
        assert StageTwoTokenType.IN in types

    def test_or_does_not_steal_from_ordinary(self):
        tokens = _parse("o")
        assert _types(tokens) == [StageTwoTokenType.O_LOWERCASE]


class TestIncompleteKeywords:
    def test_incomplete_false(self):
        tokens = _parse("fals")
        types = _types(tokens)
        assert StageTwoTokenType.FALSE not in types
        assert all(len(t.token_type.value) == 1 for t in tokens)

    def test_incomplete_while(self):
        tokens = _parse("whil")
        types = _types(tokens)
        assert StageTwoTokenType.WHILE not in types

    def test_single_f(self):
        tokens = _parse("f")
        assert _types(tokens) == [StageTwoTokenType.F_LOWERCASE]

    def test_incomplete_then_space(self):
        tokens = _parse("fals ")
        types = _types(tokens)
        assert StageTwoTokenType.FALSE not in types


class TestMultipleKeywordsInSequence:
    def test_two_keywords_space_separated(self):
        tokens = _parse("if for")
        types = _types(tokens)
        assert types == [
            StageTwoTokenType.IF,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.FOR,
        ]

    def test_three_keywords(self):
        tokens = _parse("for in while")
        types = _types(tokens)
        assert types == [
            StageTwoTokenType.FOR,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.IN,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.WHILE,
        ]

    def test_keywords_with_identifiers(self):
        tokens = _parse("x for y in z")
        types = _types(tokens)
        assert types == [
            StageTwoTokenType.X_LOWERCASE,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.FOR,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.Y_LOWERCASE,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.IN,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.Z_LOWERCASE,
        ]


class TestPositionTracking:
    def test_keyword_position(self):
        tokens = _parse("for")
        assert tokens[0].position == Position(line=1, column=0)

    def test_keyword_after_space(self):
        tokens = _parse(" for")
        for_token = next(t for t in tokens if t.token_type == StageTwoTokenType.FOR)
        assert for_token.position == Position(line=1, column=1)

    def test_passthrough_positions(self):
        tokens = _parse("ab")
        assert tokens[0].position == Position(line=1, column=0)
        assert tokens[1].position == Position(line=1, column=1)

    def test_rejected_keyword_preserves_char_positions(self):
        tokens = _parse("forl")
        assert tokens[0].position == Position(line=1, column=0)
        assert tokens[1].position == Position(line=1, column=1)
        assert tokens[2].position == Position(line=1, column=2)
        assert tokens[3].position == Position(line=1, column=3)


class TestEmptyInput:
    def test_empty_string(self):
        tokens = _parse("")
        assert tokens == []


class TestBackToBackKeywords:
    def test_adjacent_keywords_no_space(self):
        tokens = _parse("forfor")
        types = _types(tokens)
        assert StageTwoTokenType.FOR not in types
        assert all(len(t.token_type.value) == 1 for t in tokens)

    def test_keyword_then_keyword_different(self):
        tokens = _parse("forif")
        types = _types(tokens)
        assert StageTwoTokenType.FOR not in types
        assert StageTwoTokenType.IF not in types


class TestStringLiterals:
    def test_double_quoted_string(self):
        tokens = _parse('"hello"')
        assert len(tokens) == 1
        assert tokens[0].token_type == StageTwoTokenType.STRING
        assert isinstance(tokens[0], StringLiteralStageTwoToken)

    def test_single_quoted_string(self):
        tokens = _parse("'hello'")
        assert len(tokens) == 1
        assert tokens[0].token_type == StageTwoTokenType.STRING
        assert isinstance(tokens[0], StringLiteralStageTwoToken)

    def test_string_preserves_inner_tokens(self):
        tokens = _parse('"abc"')
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        inner_values = "".join(t.token_type.value for t in tokens[0].value)
        assert inner_values == '"abc"'

    def test_string_with_keyword_inside(self):
        tokens = _parse('"for"')
        assert len(tokens) == 1
        assert tokens[0].token_type == StageTwoTokenType.STRING

    def test_string_between_keywords(self):
        tokens = _parse('for "hello" if')
        types = _types(tokens)
        assert types == [
            StageTwoTokenType.FOR,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.STRING,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.IF,
        ]

    def test_string_position(self):
        tokens = _parse('"hi"')
        assert tokens[0].position == Position(line=1, column=0)

    def test_string_after_space(self):
        tokens = _parse(' "hi"')
        string_token = next(t for t in tokens if t.token_type == StageTwoTokenType.STRING)
        assert string_token.position == Position(line=1, column=1)

    def test_empty_string(self):
        tokens = _parse('""')
        assert len(tokens) == 1
        assert tokens[0].token_type == StageTwoTokenType.STRING
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        inner_values = "".join(t.token_type.value for t in tokens[0].value)
        assert inner_values == '""'

    def test_unterminated_string_consumes_rest(self):
        tokens = _parse('"hello')
        assert len(tokens) == 1
        assert tokens[0].token_type == StageTwoTokenType.STRING
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        inner_values = "".join(t.token_type.value for t in tokens[0].value)
        assert inner_values == '"hello'

    def test_string_with_spaces(self):
        tokens = _parse('"hello world"')
        assert len(tokens) == 1
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        inner_values = "".join(t.token_type.value for t in tokens[0].value)
        assert inner_values == '"hello world"'

    def test_string_with_newline(self):
        tokens = _parse('"hello\nworld"')
        assert len(tokens) == 1
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        inner_values = "".join(t.token_type.value for t in tokens[0].value)
        assert inner_values == '"hello\nworld"'

    def test_multiple_strings(self):
        tokens = _parse('"a" "b"')
        types = _types(tokens)
        assert types == [
            StageTwoTokenType.STRING,
            StageTwoTokenType.SPACE,
            StageTwoTokenType.STRING,
        ]

    def test_escaped_double_quote(self):
        tokens = _parse(r'"hello\"world"')
        assert len(tokens) == 1
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        inner_values = "".join(t.token_type.value for t in tokens[0].value)
        assert inner_values == r'"hello\"world"'

    def test_escaped_single_quote(self):
        tokens = _parse(r"'hello\'world'")
        assert len(tokens) == 1
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        inner_values = "".join(t.token_type.value for t in tokens[0].value)
        assert inner_values == r"'hello\'world'"

    def test_escaped_backslash_before_quote(self):
        tokens = _parse(r'"hello\\"')
        assert len(tokens) == 1
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        inner_values = "".join(t.token_type.value for t in tokens[0].value)
        assert inner_values == r'"hello\\"'

    def test_escaped_backslash_then_escaped_quote(self):
        tokens = _parse(r'"a\\\"b"')
        assert len(tokens) == 1
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        inner_values = "".join(t.token_type.value for t in tokens[0].value)
        assert inner_values == r'"a\\\"b"'
