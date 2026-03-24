# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from dependency_injector import containers, providers

from spud.di.logging import create_logger


class Container(containers.DeclarativeContainer):
    logger = providers.Factory(create_logger)
