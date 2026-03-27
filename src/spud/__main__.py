# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from pathlib import Path

import cyclopts
from dependency_injector import providers

from spud.core.file_reader import FileReader
from spud.di import Container
from spud.stage_six.parse_error import ParseError

app = cyclopts.App()

container = Container()


@app.default
def main(file: Path, tree: bool = False) -> None:
    container.reader.override(providers.Factory(FileReader, path=file))
    stage_six = container.stage_six()
    result = stage_six.parse()
    match result:
        case ParseError():
            print(result)
        case program if tree:
            from spud.core.ast_printer import print_ast

            print_ast(program)
        case program:
            print(program)


def entrypoint() -> None:
    app()


if __name__ == "__main__":
    entrypoint()
