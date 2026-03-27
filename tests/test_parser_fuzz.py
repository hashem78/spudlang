"""Property-based fuzz testing for the parser.

Uses Hypothesis to generate random inputs and verify the parser
never crashes, never loops, and always returns a valid Program.
"""

from datetime import timedelta
from typing import Generator

import structlog
from hypothesis import given, settings
from hypothesis import strategies as st

from spud.di.container import _create_parsers
from spud.di.stage_four_trie import create_stage_four_trie
from spud.di.stage_two_trie import create_stage_two_trie
from spud.stage_five.stage_five import StageFive
from spud.stage_four.stage_four import StageFour
from spud.stage_one.stage_one import StageOne
from spud.stage_six.program import Program
from spud.stage_six.token_stream import TokenStream
from spud.stage_three.stage_three import StageThree
from spud.stage_two.stage_two import StageTwo

_S2_TRIE = create_stage_two_trie()
_S4_TRIE = create_stage_four_trie()
_PROGRAM_PARSER = _create_parsers()["program_parser"]
_LOGGER = structlog.get_logger()


class _StringReader:
    def __init__(self, text: str):
        self._text = text

    def read(self) -> Generator[str, None, None]:
        yield from self._text


def _parse(text: str) -> Program:
    reader = _StringReader(text)
    s1 = StageOne(reader)
    s2 = StageTwo(s1, _S2_TRIE, _LOGGER)
    s3 = StageThree(s2, _LOGGER)
    s4 = StageFour(s3, _S4_TRIE, _LOGGER)
    s5 = StageFive(s4, _LOGGER)
    tokens = list(s5.parse())
    stream = TokenStream(tokens)
    return _PROGRAM_PARSER.parse(stream)


_SPUD_TOKENS: list[str] = [
    "x",
    "y",
    "z",
    "foo",
    "bar",
    "baz",
    "0",
    "1",
    "42",
    "100",
    ":=",
    "=>",
    "=",
    "==",
    "!=",
    "<",
    ">",
    "<=",
    ">=",
    "+",
    "-",
    "*",
    "/",
    "%",
    "&&",
    "||",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    ",",
    ".",
    ":",
    ";",
    "if",
    "elif",
    "else",
    "for",
    "in",
    "true",
    "false",
    '"hello"',
    '"world"',
    "'test'",
    "`raw`",
    '"unterminated',
    "'unterminated",
    "`unterminated",
    "\n",
    "\n  ",
    "\n    ",
    "\n      ",
    " ",
]

_token_soup: st.SearchStrategy[str] = st.lists(
    st.sampled_from(_SPUD_TOKENS),
    min_size=0,
    max_size=30,
).map("".join)

_VALID_SNIPPETS: list[str] = [
    "x := 5",
    "y := 10",
    'name := "spud"',
    "flag := true",
    "foo()",
    "bar(1, 2)",
    "a + b",
    "a + b * c",
    "f := (x) =>\n  x + 1",
    "if x > 0\n  true\nelse\n  false",
    "for i in items\n  process(i)",
]

_corrupted_programs: st.SearchStrategy[str] = st.lists(
    st.one_of(
        st.sampled_from(_VALID_SNIPPETS),
        st.sampled_from([":=", "else", "elif", "for", "if", "(", '"unterminated', ")"]),
    ),
    min_size=1,
    max_size=8,
).map("\n".join)


class TestParserNeverCrashes:
    @given(st.text(max_size=200))
    @settings(max_examples=500, deadline=timedelta(seconds=10))
    def test_random_text(self, text: str) -> None:
        result = _parse(text)
        assert isinstance(result, Program)
        assert isinstance(result.body, list)
        assert isinstance(result.errors, list)

    @given(_token_soup)
    @settings(max_examples=500, deadline=timedelta(seconds=5))
    def test_token_soup(self, text: str) -> None:
        result = _parse(text)
        assert isinstance(result, Program)
        assert isinstance(result.body, list)
        assert isinstance(result.errors, list)

    @given(_corrupted_programs)
    @settings(max_examples=500, deadline=timedelta(seconds=5))
    def test_corrupted_programs(self, text: str) -> None:
        result = _parse(text)
        assert isinstance(result, Program)
        assert isinstance(result.body, list)
        assert isinstance(result.errors, list)


class TestRecoveryProperties:
    @given(_corrupted_programs)
    @settings(max_examples=200, deadline=timedelta(seconds=5))
    def test_valid_statements_survive_corruption(self, text: str) -> None:
        result = _parse(text)
        assert isinstance(result, Program)
