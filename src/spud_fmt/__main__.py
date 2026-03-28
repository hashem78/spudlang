import sys
from pathlib import Path

import cyclopts
from dependency_injector import providers

from spud.core.file_reader import FileReader
from spud.core.stdin_reader import StdinReader
from spud_fmt.config_loader import load_config
from spud_fmt.container import FmtContainer

app = cyclopts.App()

container = FmtContainer()


@app.default
def main(file: Path | None = None, *, write: bool = False, config: Path | None = None) -> None:
    fmt_config = load_config(file or Path("."), config)
    container.config.override(providers.Object(fmt_config))

    if file is not None:
        container.reader.override(providers.Factory(FileReader, path=file))
    else:
        container.reader.override(providers.Factory(StdinReader))

    stage_six = container.stage_six()
    program = stage_six.parse()

    for error in program.errors:
        print(f"error: {error.kind.value} at {error.position.line}:{error.position.column}", file=sys.stderr)

    formatter = container.formatter()
    formatted = formatter.format_program(program)

    if write and file is not None:
        file.write_text(formatted)
    else:
        sys.stdout.write(formatted)


def entrypoint() -> None:
    app()


if __name__ == "__main__":
    entrypoint()
