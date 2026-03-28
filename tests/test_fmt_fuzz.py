# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Fuzz testing for the formatter.

Generates random valid spud programs, formats them, re-parses the
formatted output, and verifies the round-trip produces no errors.
"""

from datetime import timedelta

from hypothesis import given, settings
from hypothesis import strategies as st

from spud_fmt.config import FmtConfig, QuoteStyle
from spud_fmt.container import _create_formatter
from tests.fuzz_helpers import load_valid_golden_programs, parse_text

_VALID_PROGRAMS = [
    "x := 1",
    "y := 2\nz := 3",
    'name := "spud"',
    "flag := true",
    "result := a + b",
    "x := a + b * c",
    "foo()",
    "bar(1, 2)",
    'greet("world")',
    "f := (x) =>\n  x + 1",
    "add := (a, b) =>\n  result := a + b\n  result",
    "if x > 0\n  true",
    "if x > 0\n  true\nelse\n  false",
    "if x > 0\n  true\nelif x < 0\n  false\nelse\n  0",
    "for i in range(10)\n  print(i)",
    "for x in items\n  if x > 0\n    process(x)",
    "x := 1\n\nf := (a) =>\n  a + 1\n\ny := f(x)",
    *load_valid_golden_programs(),
]

_valid_programs = st.sampled_from(_VALID_PROGRAMS)

# Strategy: combine multiple valid programs into one
_multi_programs = st.lists(st.sampled_from(_VALID_PROGRAMS), min_size=1, max_size=5).map("\n".join)

# Strategy: random config variations
_random_config = st.builds(
    FmtConfig,
    indent_size=st.sampled_from([2, 4, 8]),
    quote_style=st.sampled_from([QuoteStyle.SINGLE, QuoteStyle.DOUBLE]),
    blank_lines_around_blocks=st.booleans(),
    spaces_around_operators=st.booleans(),
    spaces_around_walrus=st.booleans(),
    spaces_around_fat_arrow=st.booleans(),
    space_after_comma=st.booleans(),
    trailing_newline=st.booleans(),
)


class TestFormatterNeverCrashes:
    @given(_valid_programs)
    @settings(max_examples=200, deadline=timedelta(seconds=10))
    def test_format_valid_programs(self, text: str) -> None:
        program = parse_text(text)
        assert len(program.errors) == 0
        formatter = _create_formatter(FmtConfig())
        result = formatter.format_program(program)
        assert isinstance(result, str)
        assert len(result) > 0

    @given(_multi_programs)
    @settings(max_examples=200, deadline=timedelta(seconds=10))
    def test_format_combined_programs(self, text: str) -> None:
        program = parse_text(text)
        if program.errors:
            return
        formatter = _create_formatter(FmtConfig())
        result = formatter.format_program(program)
        assert isinstance(result, str)

    @given(_valid_programs, _random_config)
    @settings(max_examples=300, deadline=timedelta(seconds=10))
    def test_format_with_random_config(self, text: str, config: FmtConfig) -> None:
        """Every config combination should produce valid output, never crash."""
        program = parse_text(text)
        if program.errors:
            return
        formatter = _create_formatter(config)
        result = formatter.format_program(program)
        assert isinstance(result, str)


class TestRoundTrip:
    @given(_valid_programs)
    @settings(max_examples=200, deadline=timedelta(seconds=10))
    def test_format_then_reparse_no_errors(self, text: str) -> None:
        """Format a program, parse the output, verify no errors."""
        program = parse_text(text)
        if program.errors:
            return
        formatter = _create_formatter(FmtConfig())
        formatted = formatter.format_program(program)
        reparsed = parse_text(formatted)
        assert len(reparsed.errors) == 0, f"Round-trip errors: {reparsed.errors}\nFormatted:\n{formatted}"

    @given(_valid_programs)
    @settings(max_examples=200, deadline=timedelta(seconds=10))
    def test_idempotent(self, text: str) -> None:
        """Format twice — output should be identical."""
        program = parse_text(text)
        if program.errors:
            return
        formatter = _create_formatter(FmtConfig())
        first = formatter.format_program(program)
        reparsed = parse_text(first)
        if reparsed.errors:
            return
        second = formatter.format_program(reparsed)
        assert first == second, f"Not idempotent:\nFirst:\n{first}\nSecond:\n{second}"

    @given(_multi_programs)
    @settings(max_examples=200, deadline=timedelta(seconds=10))
    def test_combined_round_trip(self, text: str) -> None:
        """Combined programs should also round-trip cleanly."""
        program = parse_text(text)
        if program.errors:
            return
        formatter = _create_formatter(FmtConfig())
        formatted = formatter.format_program(program)
        reparsed = parse_text(formatted)
        assert len(reparsed.errors) == 0

    @given(_valid_programs, _random_config)
    @settings(max_examples=200, deadline=timedelta(seconds=10))
    def test_idempotent_with_random_config(self, text: str, config: FmtConfig) -> None:
        """Idempotency holds for any config."""
        program = parse_text(text)
        if program.errors:
            return
        formatter = _create_formatter(config)
        first = formatter.format_program(program)
        reparsed = parse_text(first)
        if reparsed.errors:
            return
        second = formatter.format_program(reparsed)
        assert first == second
