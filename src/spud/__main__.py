# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

import cyclopts

from spud.di import Container

app = cyclopts.App()


@app.default
def main() -> None:
    pass


def entrypoint() -> None:
    container = Container()
    container.wire(modules=[__name__])
    app()


if __name__ == "__main__":
    entrypoint()
