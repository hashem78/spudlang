# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from pathlib import Path

import cyclopts

from spud.core.file_reader import FileReader
from spud.di import Container

app = cyclopts.App()

container = Container()


@app.default
def main(file: Path, tree: bool = False, env: bool = False) -> None:
    pipeline = container.pipeline()
    result = pipeline.run(FileReader(file))
    for error in result.program.errors:
        print(f"error: {error}")
    if tree:
        from spud.core.ast_printer import print_ast

        print_ast(result.program)
    elif env:
        from spud.core.environment_printer import print_environment

        print_environment(result.resolve_result.environment)
    else:
        print(result.program)


def entrypoint() -> None:
    app()


if __name__ == "__main__":
    entrypoint()
