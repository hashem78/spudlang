# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import structlog

from spud.core.file_reader import FileReader
from spud.core.string_reader import StringReader
from spud.di.container import _create_program_parser
from spud.di.stage_four_trie import create_stage_four_trie
from spud.di.stage_two_trie import create_stage_two_trie
from spud.stage_five.stage_five import StageFive
from spud.stage_four.stage_four import StageFour
from spud.stage_one.stage_one import StageOne
from spud.stage_six.token_stream import TokenStream
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
        value = token.value.replace("\n", r"\n")
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
        value = token.value.replace("\n", r"\n")
        lines.append(f"{token.token_type.name} {value}")
    return "\n".join(lines)


def _serialize_stage_five(path: Path) -> str:
    reader = FileReader(path)
    stage_one = StageOne(reader)
    stage_two = StageTwo(stage_one, STAGE_TWO_TRIE, LOGGER)
    stage_three = StageThree(stage_two, LOGGER)
    stage_four = StageFour(stage_three, STAGE_FOUR_TRIE, LOGGER)
    stage_five = StageFive(stage_four, LOGGER)
    lines = []
    for token in stage_five.parse():
        value = token.value.replace("\n", r"\n")
        lines.append(f"{token.token_type.name} {value}")
    return "\n".join(lines)


_PROGRAM_PARSER = _create_program_parser()


def _serialize_stage_six(path: Path) -> str:
    import io

    import yaml

    reader = FileReader(path)
    stage_one = StageOne(reader)
    stage_two = StageTwo(stage_one, STAGE_TWO_TRIE, LOGGER)
    stage_three = StageThree(stage_two, LOGGER)
    stage_four = StageFour(stage_three, STAGE_FOUR_TRIE, LOGGER)
    stage_five = StageFive(stage_four, LOGGER)
    tokens = list(stage_five.parse())
    stream = TokenStream(tokens)
    program = _PROGRAM_PARSER.parse(stream)

    errors = []
    for error in program.errors:
        entry: dict[str, str] = {
            "position": f"{error.position.line}:{error.position.column}",
            "kind": error.kind.value,
        }
        if error.got:
            entry["got"] = error.got.value
        if error.expected:
            entry["expected"] = error.expected.value
        if error.context:
            entry["context"] = error.context.kind.value
        errors.append(entry)

    buf = io.StringIO()
    for i, node in enumerate(program.body):
        is_last = i == len(program.body) - 1
        _print_node_to_buf(node, "", is_last, buf)
    tree = buf.getvalue().rstrip("\n")

    class _LiteralStr(str):
        pass

    def _literal_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")

    dumper = yaml.Dumper
    dumper.add_representer(_LiteralStr, _literal_representer)

    result: dict = {"errors": errors, "tree": _LiteralStr(tree) if tree else ""}
    return yaml.dump(result, Dumper=dumper, default_flow_style=False, sort_keys=False, allow_unicode=True).rstrip("\n")


def _print_node_to_buf(node, prefix: str, is_last: bool, buf) -> None:
    from spud.core.ast_printer import _children, _label

    connector = "\u2514\u2500\u2500 " if is_last else "\u251c\u2500\u2500 "
    child_prefix = prefix + ("    " if is_last else "\u2502   ")
    buf.write(f"{prefix}{connector}{_label(node)}\n")
    for i, child in enumerate(_children(node)):
        _print_node_to_buf(child, child_prefix, i == len(_children(node)) - 1, buf)


def _serialize_fmt(path: Path) -> str:
    """Parse and format a spud file, return the formatted source."""
    from spud_fmt.config import FmtConfig
    from spud_fmt.container import _create_formatter

    text = path.read_text()
    reader = StringReader(text)
    stage_one = StageOne(reader)
    stage_two = StageTwo(stage_one, STAGE_TWO_TRIE, LOGGER)
    stage_three = StageThree(stage_two, LOGGER)
    stage_four = StageFour(stage_three, STAGE_FOUR_TRIE, LOGGER)
    stage_five = StageFive(stage_four, LOGGER)
    tokens = list(stage_five.parse())
    stream = TokenStream(tokens)
    program = _PROGRAM_PARSER.parse(stream)
    if program.errors:
        return text.rstrip("\n")
    formatter = _create_formatter(FmtConfig())
    return formatter.format_program(program).rstrip("\n")


def _run_case(spud_path: Path, serializer, expected_suffix: str = ".expected") -> tuple[str, str | None]:
    """Run a single golden test case. Returns (name, failure_message or None)."""
    name = f"{spud_path.parent.name}/{spud_path.stem}"
    expected_path = spud_path.with_suffix(expected_suffix)

    if not expected_path.exists():
        return name, f"Missing expected file: {expected_path}"

    actual = serializer(spud_path)
    expected = expected_path.read_text().rstrip("\n")

    if actual != expected:
        return name, f"  expected:\n{expected}\n  actual:\n{actual}"

    return name, None


def _run_stage(
    stage_dir: Path, serializer, expected_suffix: str = ".expected"
) -> tuple[int, int, list[tuple[str, str]]]:
    """Run all cases in a stage directory in parallel. Returns (passed, total, failures)."""
    spud_files = sorted(stage_dir.glob("*.spud"))
    failures: list[tuple[str, str]] = []
    passed = 0

    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(_run_case, spud_path, serializer, expected_suffix): spud_path for spud_path in spud_files
        }
        for future in as_completed(futures):
            name, failure = future.result()
            if failure is None:
                passed += 1
            else:
                failures.append((name, failure))

    return passed, len(spud_files), failures


def main() -> int:
    stages: list[tuple[str, Path, object, str]] = [
        ("Stage One", GOLDEN_DIR / "stage_one", _serialize_stage_one, ".expected"),
        ("Stage Two", GOLDEN_DIR / "stage_two", _serialize_stage_two, ".expected"),
        ("Stage Three", GOLDEN_DIR / "stage_three", _serialize_stage_three, ".expected"),
        ("Stage Four", GOLDEN_DIR / "stage_four", _serialize_stage_four, ".expected"),
        ("Stage Five", GOLDEN_DIR / "stage_five", _serialize_stage_five, ".expected"),
        ("Stage Six", GOLDEN_DIR / "stage_six", _serialize_stage_six, ".expected.yaml"),
        ("Formatter", GOLDEN_DIR / "fmt", _serialize_fmt, ".expected"),
    ]

    all_failures: list[tuple[str, str]] = []
    results: list[tuple[str, int, int]] = []

    for stage_name, stage_dir, serializer, suffix in stages:
        if not stage_dir.exists():
            results.append((stage_name, 0, 0))
            continue
        passed, total, failures = _run_stage(stage_dir, serializer, suffix)
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
