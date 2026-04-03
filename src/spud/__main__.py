# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from pathlib import Path

import cyclopts
from dependency_injector import providers

from spud.core.file_reader import FileReader
from spud.di import Container

app = cyclopts.App()

container = Container()


@app.default
def main(file: Path, tree: bool = False, env: bool = False) -> None:
    container.reader.override(providers.Factory(FileReader, path=file))
    stage_six = container.stage_six()
    program = stage_six.parse()
    for error in program.errors:
        print(f"error: {error}")
    if tree:
        from spud.core.ast_printer import print_ast

        print_ast(program)
    elif env:
        stage_seven = container.stage_seven()
        result = stage_seven.resolve(program)
        for error in result.errors:
            print(f"resolve error: {error.kind.value} '{error.name}' at {error.position.line}:{error.position.column}")

        from spud.core.environment_printer import print_environment

        print_environment(result.environment)
    else:
        print(program)


def entrypoint() -> None:
    app()


if __name__ == "__main__":
    entrypoint()
