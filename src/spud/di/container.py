# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from dependency_injector import containers, providers

from spud.core.stdin_reader import StdinReader
from spud.di.logging import create_logger
from spud.di.stage_two_trie import create_stage_two_trie
from spud.stage_one.stage_one import StageOne
from spud.stage_three.stage_three import StageThree
from spud.stage_two.stage_two import StageTwo


class Container(containers.DeclarativeContainer):
    logger = providers.Factory(create_logger)

    reader = providers.Factory(StdinReader)
    stage_one = providers.Factory(StageOne, handle=reader)
    stage_two_trie = providers.Singleton(create_stage_two_trie)
    stage_two = providers.Factory(StageTwo, stage_one=stage_one, trie=stage_two_trie, logger=logger)
    stage_three = providers.Factory(StageThree, stage_two=stage_two, logger=logger)
