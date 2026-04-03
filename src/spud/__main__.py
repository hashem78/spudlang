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
    program = container.stage_six().parse()
    result = container.stage_seven().resolve(program)
    program = result.program
    for error in program.errors:
        print(f"error: {error}")
    if tree:
        from spud.core.ast_printer import print_ast

        print_ast(program)
    elif env:
        from spud.core.environment_printer import print_environment

        print_environment(result.environment)
    else:
        print(program)


def entrypoint() -> None:
    app()


if __name__ == "__main__":
    entrypoint()
