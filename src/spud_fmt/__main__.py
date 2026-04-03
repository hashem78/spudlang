import sys
from pathlib import Path

import cyclopts
from dependency_injector import providers

from spud.core.pipeline import ParsedProgram
from spud.core.string_reader import StringReader
from spud_fmt.config_loader import load_config
from spud_fmt.container import FmtContainer

app = cyclopts.App()

container = FmtContainer()


@app.default
def main(file: Path | None = None, *, write: bool = False, config: Path | None = None) -> None:
    fmt_config = load_config(file or Path("."), config)
    container.config.override(providers.Object(fmt_config))

    if file is not None:
        original = file.read_text()
    else:
        original = sys.stdin.read()

    pipeline = container.pipeline()
    parsed = pipeline.get(ParsedProgram, StringReader(original))

    if parsed.program.errors:
        for error in parsed.program.errors:
            print(f"error: {error}", file=sys.stderr)
        sys.stdout.write(original)
        sys.exit(1)

    formatter = container.formatter()
    formatted = formatter.format_program(parsed.program)

    if write and file is not None:
        file.write_text(formatted)
    else:
        sys.stdout.write(formatted)


def entrypoint() -> None:
    app()


if __name__ == "__main__":
    entrypoint()
