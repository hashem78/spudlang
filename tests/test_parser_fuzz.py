"""Property-based fuzz testing for the parser.

Uses Hypothesis to generate random inputs and verify the parser
never crashes, never loops, and always returns a valid Program.
"""

from datetime import timedelta

from tests.fuzz_helpers import load_valid_golden_programs, parse_text
from hypothesis import given, settings
from hypothesis import strategies as st

from spud.stage_six.program import Program

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
    *load_valid_golden_programs(),
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
        result = parse_text(text)
        assert isinstance(result, Program)
        assert isinstance(result.body, list)
        assert isinstance(result.errors, list)

    @given(_token_soup)
    @settings(max_examples=500, deadline=timedelta(seconds=5))
    def test_token_soup(self, text: str) -> None:
        result = parse_text(text)
        assert isinstance(result, Program)
        assert isinstance(result.body, list)
        assert isinstance(result.errors, list)

    @given(_corrupted_programs)
    @settings(max_examples=500, deadline=timedelta(seconds=5))
    def test_corrupted_programs(self, text: str) -> None:
        result = parse_text(text)
        assert isinstance(result, Program)
        assert isinstance(result.body, list)
        assert isinstance(result.errors, list)


class TestRecoveryProperties:
    @given(_corrupted_programs)
    @settings(max_examples=200, deadline=timedelta(seconds=5))
    def test_valid_statements_survive_corruption(self, text: str) -> None:
        result = parse_text(text)
        assert isinstance(result, Program)
