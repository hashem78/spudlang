"""Shared helpers for fuzz test files."""

from pathlib import Path

import structlog

from spud.core.string_reader import StringReader
from spud.di.container import _create_program_parser
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
_PROGRAM_PARSER = _create_program_parser()
_LOGGER = structlog.get_logger()
_GOLDEN_DIR = Path(__file__).parent / "golden"


def parse_text(text: str) -> Program:
    reader = StringReader(text)
    s1 = StageOne(reader)
    s2 = StageTwo(s1, _S2_TRIE, _LOGGER)
    s3 = StageThree(s2, _LOGGER)
    s4 = StageFour(s3, _S4_TRIE, _LOGGER)
    s5 = StageFive(s4, _LOGGER)
    tokens = list(s5.parse())
    stream = TokenStream(tokens)
    return _PROGRAM_PARSER.parse(stream)


def load_valid_golden_programs() -> list[str]:
    """Load golden .spud files that parse without errors."""
    programs: list[str] = []
    for subdir in ["fmt", "stage_six", "stage_five"]:
        d = _GOLDEN_DIR / subdir
        if not d.exists():
            continue
        for f in sorted(d.glob("*.spud")):
            if "recovery" in f.name:
                continue
            text = f.read_text()
            if not parse_text(text).errors:
                programs.append(text)
    return programs
