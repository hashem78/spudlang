# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import structlog

from spud.core.file_reader import FileReader
from spud.di.stage_four_trie import create_stage_four_trie
from spud.di.stage_two_trie import create_stage_two_trie
from spud.stage_four.stage_four import StageFour
from spud.stage_one.stage_one import StageOne
from spud.stage_three.stage_three import StageThree
from spud.stage_two.stage_two import StageTwo

GOLDEN_DIR = Path(__file__).parent / "golden"
STAGE_TWO_TRIE = create_stage_two_trie()
STAGE_FOUR_TRIE = create_stage_four_trie()
LOGGER = structlog.get_logger()


def _serialize_stage_one(path: Path) -> str:
    reader = FileReader(path)
    stage_one = StageOne(reader)
    return "\n".join(token.token_type.name for token in stage_one.parse())


def _serialize_stage_two(path: Path) -> str:
    reader = FileReader(path)
    stage_one = StageOne(reader)
    stage_two = StageTwo(stage_one, STAGE_TWO_TRIE, LOGGER)
    return "\n".join(token.token_type.name for token in stage_two.parse())


def _serialize_stage_three(path: Path) -> str:
    reader = FileReader(path)
    stage_one = StageOne(reader)
    stage_two = StageTwo(stage_one, STAGE_TWO_TRIE, LOGGER)
    stage_three = StageThree(stage_two, LOGGER)
    lines = []
    for token in stage_three.parse():
        value = r"\n" if token.value == "\n" else token.value
        lines.append(f"{token.token_type.name} {value}")
    return "\n".join(lines)


def _serialize_stage_four(path: Path) -> str:
    reader = FileReader(path)
    stage_one = StageOne(reader)
    stage_two = StageTwo(stage_one, STAGE_TWO_TRIE, LOGGER)
    stage_three = StageThree(stage_two, LOGGER)
    stage_four = StageFour(stage_three, STAGE_FOUR_TRIE, LOGGER)
    lines = []
    for token in stage_four.parse():
        value = r"\n" if token.value == "\n" else token.value
        lines.append(f"{token.token_type.name} {value}")
    return "\n".join(lines)


def _run_case(spud_path: Path, serializer) -> tuple[str, str | None]:
    """Run a single golden test case. Returns (name, failure_message or None)."""
    name = f"{spud_path.parent.name}/{spud_path.stem}"
    expected_path = spud_path.with_suffix(".expected")

    if not expected_path.exists():
        return name, f"Missing expected file: {expected_path}"

    actual = serializer(spud_path)
    expected = expected_path.read_text().rstrip("\n")

    if actual != expected:
        return name, f"  expected:\n{expected}\n  actual:\n{actual}"

    return name, None


def _run_stage(stage_dir: Path, serializer) -> tuple[int, int, list[tuple[str, str]]]:
    """Run all cases in a stage directory in parallel. Returns (passed, total, failures)."""
    spud_files = sorted(stage_dir.glob("*.spud"))
    failures: list[tuple[str, str]] = []
    passed = 0

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(_run_case, spud_path, serializer): spud_path for spud_path in spud_files}
        for future in as_completed(futures):
            name, failure = future.result()
            if failure is None:
                passed += 1
            else:
                failures.append((name, failure))

    return passed, len(spud_files), failures


def main() -> int:
    stages = [
        ("Stage One", GOLDEN_DIR / "stage_one", _serialize_stage_one),
        ("Stage Two", GOLDEN_DIR / "stage_two", _serialize_stage_two),
        ("Stage Three", GOLDEN_DIR / "stage_three", _serialize_stage_three),
        ("Stage Four", GOLDEN_DIR / "stage_four", _serialize_stage_four),
    ]

    all_failures: list[tuple[str, str]] = []
    results: list[tuple[str, int, int]] = []

    for stage_name, stage_dir, serializer in stages:
        if not stage_dir.exists():
            results.append((stage_name, 0, 0))
            continue
        passed, total, failures = _run_stage(stage_dir, serializer)
        results.append((stage_name, passed, total))
        all_failures.extend(failures)

    if all_failures:
        print("\nFAILURES:\n")
        for name, message in all_failures:
            print(f"FAIL {name}")
            print(message)
            print()

    max_name_len = max(len(name) for name, _, _ in results)
    print("\nSummary:\n")
    for stage_name, passed, total in results:
        status = "PASS" if passed == total else "FAIL"
        print(f"  {stage_name:<{max_name_len}}  {passed}/{total} passed  [{status}]")

    print()
    return 1 if all_failures else 0


if __name__ == "__main__":
    sys.exit(main())
