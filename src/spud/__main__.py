# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from dependency_injector.wiring import Provide, inject

from spud.di import Container


@inject
def main(logger=Provide[Container.logger]) -> None:
    logger.info("Hello World!")


def entrypoint() -> None:
    container = Container()
    container.wire(modules=[__name__])
    main()


if __name__ == "__main__":
    entrypoint()
