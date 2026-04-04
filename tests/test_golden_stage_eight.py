# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from spud.core.file_reader import FileReader
from spud.core.pipeline import Pipeline
from spud.di.container import Container
from spud.stage_eight.type_errors.argument_count_mismatch_error import ArgumentCountMismatchError
from spud.stage_eight.type_errors.argument_type_mismatch_error import ArgumentTypeMismatchError
from spud.stage_eight.type_errors.branch_type_mismatch_error import BranchTypeMismatchError
from spud.stage_eight.type_errors.condition_not_bool_error import ConditionNotBoolError
from spud.stage_eight.type_errors.element_type_mismatch_error import ElementTypeMismatchError
from spud.stage_eight.type_errors.heterogeneous_list_error import HeterogeneousListError
from spud.stage_eight.type_errors.not_callable_error import NotCallableError
from spud.stage_eight.type_errors.not_iterable_error import NotIterableError
from spud.stage_eight.type_errors.operator_type_error import OperatorTypeError
from spud.stage_eight.type_errors.return_type_mismatch_error import ReturnTypeMismatchError
from spud.stage_eight.type_errors.type_error import TypeError
from spud.stage_eight.type_errors.type_mismatch_error import TypeMismatchError
from spud.stage_eight.type_errors.unary_operator_type_error import UnaryOperatorTypeError
from spud.stage_eight.type_errors.unknown_type_error import UnknownTypeError

GOLDEN_DIR = Path(__file__).parent / "golden" / "stage_eight"

_CONTAINER = Container()
PIPELINE: Pipeline = _CONTAINER.pipeline()


def _serialize_error(error: TypeError) -> str:
    pos = f"{error.position.line}:{error.position.column}"
    match error:
        case TypeMismatchError(name=name, expected=expected, actual=actual):
            return f"TYPE_MISMATCH name={name} expected={expected.value} actual={actual.value} {pos}"
        case OperatorTypeError(operator=op, left=left, right=right):
            return f"OPERATOR_TYPE_ERROR op={op} left={left.value} right={right.value} {pos}"
        case ArgumentCountMismatchError(name=name, expected_count=expected, actual_count=actual):
            return f"ARGUMENT_COUNT_MISMATCH name={name} expected={expected} actual={actual} {pos}"
        case ArgumentTypeMismatchError(name=name, index=index, expected=expected, actual=actual):
            parts = f"name={name} index={index} expected={expected.value} actual={actual.value}"
            return f"ARGUMENT_TYPE_MISMATCH {parts} {pos}"
        case NotCallableError(name=name):
            return f"NOT_CALLABLE name={name} {pos}"
        case ReturnTypeMismatchError(expected=expected, actual=actual):
            return f"RETURN_TYPE_MISMATCH expected={expected.value} actual={actual.value} {pos}"
        case BranchTypeMismatchError(index=index, expected=expected, actual=actual):
            return f"BRANCH_TYPE_MISMATCH index={index} expected={expected.value} actual={actual.value} {pos}"
        case ConditionNotBoolError(actual=actual):
            return f"CONDITION_NOT_BOOL actual={actual.value} {pos}"
        case NotIterableError(actual=actual):
            return f"NOT_ITERABLE actual={actual.value} {pos}"
        case ElementTypeMismatchError(name=name, expected=expected, actual=actual):
            return f"ELEMENT_TYPE_MISMATCH name={name} expected={expected.value} actual={actual.value} {pos}"
        case UnknownTypeError(name=name):
            return f"UNKNOWN_TYPE name={name} {pos}"
        case HeterogeneousListError(index=index, expected=expected, actual=actual):
            return f"HETEROGENEOUS_LIST index={index} expected={expected.value} actual={actual.value} {pos}"
        case UnaryOperatorTypeError(operator=op, operand=operand):
            return f"UNARY_OPERATOR_TYPE_ERROR op={op} operand={operand.value} {pos}"


def _serialize_stage_eight(path: Path) -> str:
    result = PIPELINE.run(FileReader(path))
    if not result.type_check_result.errors:
        return "OK"
    return "\n".join(_serialize_error(e) for e in result.type_check_result.errors)


def _run_case(spud_path: Path) -> tuple[str, str | None]:
    name = spud_path.stem
    expected_path = spud_path.with_suffix(".expected")

    if not expected_path.exists():
        return name, f"Missing expected file: {expected_path}"

    actual = _serialize_stage_eight(spud_path)
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
    print(f"\nStage Eight  {passed}/{total} passed  [{status}]\n")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
