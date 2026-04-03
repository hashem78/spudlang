# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from spud.core.file_reader import FileReader
from spud.core.pipeline import Pipeline
from spud.di.container import Container

GOLDEN_DIR = Path(__file__).parent / "golden" / "stage_seven"

_CONTAINER = Container()
PIPELINE: Pipeline = _CONTAINER.pipeline()


def _serialize_stage_seven(path: Path) -> str:
    result = PIPELINE.run(FileReader(path))
    if not result.resolve_result.errors:
        return "OK"
    lines = []
    for error in result.resolve_result.errors:
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
