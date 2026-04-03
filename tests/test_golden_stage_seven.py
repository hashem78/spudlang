# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import structlog

from spud.core.file_reader import FileReader
from spud.di.container import _create_program_parser
from spud.di.stage_four_trie import create_stage_four_trie
from spud.di.stage_two_trie import create_stage_two_trie
from spud.stage_five.stage_five import StageFive
from spud.stage_four.stage_four import StageFour
from spud.stage_one.stage_one import StageOne
from spud.stage_seven.stage_seven import StageSeven
from spud.stage_six.token_stream import TokenStream
from spud.stage_three.stage_three import StageThree
from spud.stage_two.stage_two import StageTwo

GOLDEN_DIR = Path(__file__).parent / "golden" / "stage_seven"
STAGE_TWO_TRIE = create_stage_two_trie()
STAGE_FOUR_TRIE = create_stage_four_trie()
LOGGER = structlog.get_logger()

_PROGRAM_PARSER = _create_program_parser()
_RESOLVER = StageSeven(logger=LOGGER)


def _serialize_stage_seven(path: Path) -> str:
    reader = FileReader(path)
    stage_one = StageOne(reader)
    stage_two = StageTwo(stage_one, STAGE_TWO_TRIE, LOGGER)
    stage_three = StageThree(stage_two, LOGGER)
    stage_four = StageFour(stage_three, STAGE_FOUR_TRIE, LOGGER)
    stage_five = StageFive(stage_four, LOGGER)
    tokens = list(stage_five.parse())
    stream = TokenStream(tokens)
    program = _PROGRAM_PARSER.parse(stream)
    result = _RESOLVER.resolve(program)
    if not result.errors:
        return "OK"
    lines = []
    for error in result.errors:
        lines.append(f"{error.kind.name} {error.name} {error.position.line}:{error.position.column}")
    return "\n".join(lines)


def _run_case(spud_path: Path) -> tuple[str, str | None]:
    name = spud_path.stem
    expected_path = spud_path.with_suffix(".expected")

    if not expected_path.exists():
        return name, f"Missing expected file: {expected_path}"

    actual = _serialize_stage_seven(spud_path)
    expected = expected_path.read_text().rstrip("\n")

    if actual != expected:
        return name, f"  expected:\n{expected}\n  actual:\n{actual}"

    return name, None


def main() -> int:
    spud_files = sorted(GOLDEN_DIR.glob("*.spud"))
    failures: list[tuple[str, str]] = []
    passed = 0

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(_run_case, p): p for p in spud_files}
        for future in as_completed(futures):
            name, failure = future.result()
            if failure is None:
                passed += 1
            else:
                failures.append((name, failure))

    total = len(spud_files)

    if failures:
        print("\nFAILURES:\n")
        for name, message in sorted(failures):
            print(f"FAIL {name}")
            print(message)
            print()

    status = "PASS" if passed == total else "FAIL"
    print(f"\nStage Seven  {passed}/{total} passed  [{status}]\n")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
