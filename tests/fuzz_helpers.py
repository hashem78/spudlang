"""Shared helpers for fuzz test files."""

from pathlib import Path

from spud.core.pipeline import ParsedProgram, Pipeline
from spud.core.string_reader import StringReader
from spud.di.container import Container
from spud.stage_six.program import Program

_CONTAINER = Container()
PIPELINE: Pipeline = _CONTAINER.pipeline()
_GOLDEN_DIR = Path(__file__).parent / "golden"


def parse_text(text: str) -> Program:
    return PIPELINE.get(ParsedProgram, StringReader(text)).program


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
