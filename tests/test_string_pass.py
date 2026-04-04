# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from typing import Generator

from spud.stage_one import StageOneToken, StageOneTokenType
from spud.stage_one.stage_one import StageOne
from spud.stage_two import RawStringLiteralStageTwoToken, StageTwoTokenType, StringLiteralStageTwoToken
from spud.stage_two.string_pass import StringPass, StringPassToken


class _StringReader:
    def __init__(self, text: str):
        self._text = text

    def read(self) -> Generator[str, None, None]:
        for char in self._text:
            yield char


def _parse(text: str) -> list[StringPassToken]:
    reader = _StringReader(text)
    stage_one = StageOne(reader)
    string_pass = StringPass(stage_one)
    return list(string_pass.parse())


def _inner_text(token: StringLiteralStageTwoToken) -> str:
    return "".join(t.token_type.value for t in token.value)


class TestStringPassthrough:
    def test_plain_text_passes_through(self):
        tokens = _parse("hello")
        assert all(isinstance(t, StageOneToken) for t in tokens)
        assert len(tokens) == 5

    def test_spaces_pass_through(self):
        tokens = _parse("a b")
        assert all(isinstance(t, StageOneToken) for t in tokens)
        assert tokens[1].token_type == StageOneTokenType.SPACE

    def test_empty_input(self):
        assert _parse("") == []

    def test_newlines_pass_through(self):
        tokens = _parse("a\nb")
        assert all(isinstance(t, StageOneToken) for t in tokens)
        assert tokens[1].token_type == StageOneTokenType.NEW_LINE


class TestDoubleQuotedStrings:
    def test_basic_string(self):
        tokens = _parse('"hello"')
        assert len(tokens) == 1
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        assert _inner_text(tokens[0]) == '"hello"'

    def test_empty_string(self):
        tokens = _parse('""')
        assert len(tokens) == 1
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        assert _inner_text(tokens[0]) == '""'

    def test_string_with_spaces(self):
        tokens = _parse('"hello world"')
        assert len(tokens) == 1
        assert _inner_text(tokens[0]) == '"hello world"'

    def test_string_with_newline(self):
        tokens = _parse('"hello\nworld"')
        assert len(tokens) == 1
        assert _inner_text(tokens[0]) == '"hello\nworld"'


class TestSingleQuotedStrings:
    def test_basic_string(self):
        tokens = _parse("'hello'")
        assert len(tokens) == 1
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        assert _inner_text(tokens[0]) == "'hello'"

    def test_empty_string(self):
        tokens = _parse("''")
        assert len(tokens) == 1
        assert _inner_text(tokens[0]) == "''"


class TestEscapedQuotesInsideStrings:
    def test_escaped_double_quote(self):
        tokens = _parse(r'"hello\"world"')
        assert len(tokens) == 1
        assert _inner_text(tokens[0]) == r'"hello\"world"'

    def test_escaped_single_quote(self):
        tokens = _parse(r"'hello\'world'")
        assert len(tokens) == 1
        assert _inner_text(tokens[0]) == r"'hello\'world'"

    def test_escaped_backslash_before_closing_quote(self):
        tokens = _parse(r'"hello\\"')
        assert len(tokens) == 1
        assert _inner_text(tokens[0]) == r'"hello\\"'

    def test_escaped_backslash_then_escaped_quote(self):
        tokens = _parse(r'"a\\\"b"')
        assert len(tokens) == 1
        assert _inner_text(tokens[0]) == r'"a\\\"b"'


class TestEscapedQuotesOutsideStrings:
    def test_backslash_quote_is_two_tokens(self):
        tokens = _parse(r"\'")
        assert len(tokens) == 2
        assert all(isinstance(t, StageOneToken) for t in tokens)
        assert tokens[0].token_type == StageOneTokenType.BACKWARD_SLASH
        assert tokens[1].token_type == StageOneTokenType.SINGLE_QUOTES

    def test_backslash_double_quote_is_two_tokens(self):
        tokens = _parse(r"\"")
        assert len(tokens) == 2
        assert tokens[0].token_type == StageOneTokenType.BACKWARD_SLASH
        assert tokens[1].token_type == StageOneTokenType.DOUBLE_QUOTES

    def test_escaped_quote_in_word(self):
        tokens = _parse(r"we\'re")
        assert all(isinstance(t, StageOneToken) for t in tokens)
        assert len(tokens) == 6


class TestUnterminatedStrings:
    def test_unterminated_double_quote(self):
        tokens = _parse('"hello')
        assert len(tokens) == 1
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        assert _inner_text(tokens[0]) == '"hello'

    def test_unterminated_single_quote(self):
        tokens = _parse("'hello")
        assert len(tokens) == 1
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        assert _inner_text(tokens[0]) == "'hello"

    def test_unterminated_consumes_rest(self):
        tokens = _parse('"hello world 123')
        assert len(tokens) == 1
        assert _inner_text(tokens[0]) == '"hello world 123'


class TestMixedContent:
    def test_text_before_string(self):
        tokens = _parse('hello "world"')
        assert len(tokens) == 7
        assert all(isinstance(t, StageOneToken) for t in tokens[:6])
        assert isinstance(tokens[6], StringLiteralStageTwoToken)

    def test_text_after_string(self):
        tokens = _parse('"hello" world')
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        assert all(isinstance(t, StageOneToken) for t in tokens[1:])

    def test_multiple_strings(self):
        tokens = _parse('"a" "b"')
        strings = [t for t in tokens if isinstance(t, StringLiteralStageTwoToken)]
        assert len(strings) == 2

    def test_string_position(self):
        tokens = _parse('"hi"')
        assert isinstance(tokens[0], StringLiteralStageTwoToken)
        assert tokens[0].position.line == 0
        assert tokens[0].position.column == 0


class TestRawStrings:
    def test_basic_raw_string(self):
        tokens = _parse("`hello`")
        assert len(tokens) == 1
        assert isinstance(tokens[0], RawStringLiteralStageTwoToken)
        assert tokens[0].token_type == StageTwoTokenType.RAW_STRING
        assert _inner_text(tokens[0]) == "`hello`"

    def test_raw_string_no_escape_processing(self):
        tokens = _parse(r"`hello\"world`")
        assert len(tokens) == 1
        assert isinstance(tokens[0], RawStringLiteralStageTwoToken)
        assert _inner_text(tokens[0]) == r"`hello\"world`"

    def test_raw_string_with_newline(self):
        tokens = _parse("`hello\nworld`")
        assert len(tokens) == 1
        assert _inner_text(tokens[0]) == "`hello\nworld`"

    def test_raw_string_with_quotes_inside(self):
        tokens = _parse('`he said "hello"`')
        assert len(tokens) == 1
        assert _inner_text(tokens[0]) == '`he said "hello"`'

    def test_raw_string_with_single_quotes_inside(self):
        tokens = _parse("`it's raw`")
        assert len(tokens) == 1
        assert _inner_text(tokens[0]) == "`it's raw`"

    def test_empty_raw_string(self):
        tokens = _parse("``")
        assert len(tokens) == 1
        assert tokens[0].token_type == StageTwoTokenType.RAW_STRING
        assert _inner_text(tokens[0]) == "``"

    def test_unterminated_raw_string(self):
        tokens = _parse("`hello")
        assert len(tokens) == 1
        assert tokens[0].token_type == StageTwoTokenType.RAW_STRING
        assert _inner_text(tokens[0]) == "`hello"

    def test_raw_string_position(self):
        tokens = _parse("`hi`")
        assert tokens[0].position.line == 0
        assert tokens[0].position.column == 0

    def test_raw_string_between_identifiers(self):
        tokens = _parse("a `raw` b")
        strings = [t for t in tokens if isinstance(t, RawStringLiteralStageTwoToken)]
        assert len(strings) == 1
        assert strings[0].token_type == StageTwoTokenType.RAW_STRING
