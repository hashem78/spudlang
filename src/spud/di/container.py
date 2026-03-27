# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from dependency_injector import containers, providers

from spud.core.file_reader import FileReader
from spud.di.logging import create_logger
from spud.di.stage_four_trie import create_stage_four_trie
from spud.di.stage_two_trie import create_stage_two_trie
from spud.stage_five.stage_five import StageFive
from spud.stage_four.stage_four import StageFour
from spud.stage_one.stage_one import StageOne
from spud.stage_six.parsers.binding_parser import BindingParser
from spud.stage_six.parsers.block_parser import BlockParser
from spud.stage_six.parsers.expression_parser import ExpressionParser
from spud.stage_six.parsers.for_loop_parser import ForLoopParser
from spud.stage_six.parsers.function_def_parser import FunctionDefParser
from spud.stage_six.parsers.if_else_parser import IfElseParser
from spud.stage_six.parsers.program_parser import ProgramParser
from spud.stage_six.parsers.statement_parser import StatementParser
from spud.stage_six.stage_six import StageSix
from spud.stage_three.stage_three import StageThree
from spud.stage_two.stage_two import StageTwo


def _create_parsers() -> dict:
    """Wire parser dependency graph, resolving circular deps manually."""
    expression = ExpressionParser()
    block = BlockParser.__new__(BlockParser)
    function_def = FunctionDefParser(block_parser=block)
    binding = BindingParser(expression_parser=expression, function_def_parser=function_def)
    if_else = IfElseParser(expression_parser=expression, block_parser=block)
    for_loop = ForLoopParser(expression_parser=expression, block_parser=block)
    statement = StatementParser(
        expression_parser=expression,
        binding_parser=binding,
        if_else_parser=if_else,
        for_loop_parser=for_loop,
    )
    block.__init__(statement_parser=statement)
    program = ProgramParser(statement_parser=statement)
    return {"program_parser": program}


class Container(containers.DeclarativeContainer):
    logger = providers.Factory(create_logger)

    reader = providers.Factory(FileReader)
    stage_one = providers.Factory(StageOne, handle=reader)
    stage_two_trie = providers.Singleton(create_stage_two_trie)
    stage_two = providers.Factory(StageTwo, stage_one=stage_one, trie=stage_two_trie, logger=logger)
    stage_three = providers.Factory(StageThree, stage_two=stage_two, logger=logger)
    stage_four_trie = providers.Singleton(create_stage_four_trie)
    stage_four = providers.Factory(StageFour, stage_three=stage_three, trie=stage_four_trie, logger=logger)
    stage_five = providers.Factory(StageFive, stage_four=stage_four, logger=logger)

    _parsers = providers.Singleton(_create_parsers)
    program_parser = providers.Singleton(lambda p: p["program_parser"], _parsers)

    stage_six = providers.Factory(StageSix, stage_five=stage_five, program_parser=program_parser, logger=logger)
