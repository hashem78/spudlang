# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

import structlog

logger = structlog.get_logger(__name__)


def main() -> None:
    logger.info("Hello World!")


if __name__ == "__main__":
    main()
