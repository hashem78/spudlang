import sys
from pathlib import Path

import cyclopts

from spud.core import FileReader
from spud.core.pipeline import ResolvedProgram
from spud_check.container import CheckContainer

app = cyclopts.App()

container = CheckContainer()


@app.default
def main(file: Path) -> None:
    pipeline = container.pipeline()
    result = pipeline.get(ResolvedProgram, FileReader(file))

    for error in result.program.errors:
        print(f"error: {error}", file=sys.stderr)

    checker = container.checker()
    check_result = checker.check(result.program)

    for error in check_result.errors:
        print(f"type error: {error}", file=sys.stderr)

    if result.program.errors or check_result.errors:
        sys.exit(1)


def entrypoint() -> None:
    app()


if __name__ == "__main__":
    entrypoint()
