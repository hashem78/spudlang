# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from dependency_injector import containers, providers

from spud.core.pipeline import (
    ParsedProgram,
    ParseStep,
    Pipeline,
    ResolvedProgram,
    ResolveStep,
    StageFiveStep,
    StageFourStep,
    StageOneStep,
    StageThreeStep,
    StageTwoStep,
)
from spud.di.logging import create_logger
from spud.di.stage_four_trie import create_stage_four_trie
from spud.di.stage_two_trie import create_stage_two_trie
from spud.stage_five.stage_five import StageFive
from spud.stage_four.stage_four import StageFour
from spud.stage_one.stage_one import StageOne
from spud.stage_seven.stage_seven import StageSeven
from spud.stage_six.parsers.binding_parser import BindingParser
from spud.stage_six.parsers.block_parser import BlockParser
from spud.stage_six.parsers.expression_parser import ExpressionParser
from spud.stage_six.parsers.for_loop_parser import ForLoopParser
from spud.stage_six.parsers.function_def_parser import FunctionDefParser
from spud.stage_six.parsers.if_else_parser import IfElseParser
from spud.stage_six.parsers.program_parser import ProgramParser
from spud.stage_six.parsers.statement_parser import StatementParser
from spud.stage_three.stage_three import StageThree
from spud.stage_two.stage_two import StageTwo


def _create_program_parser() -> ProgramParser:
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
    return ProgramParser(statement_parser=statement)


def _create_pipeline(
    s2_trie: object,
    s4_trie: object,
    program_parser: ProgramParser,
    resolver: StageSeven,
    logger: object,
) -> Pipeline:
    s1 = StageOneStep()
    s2 = StageTwoStep(prev=s1, trie=s2_trie, logger=logger)
    s3 = StageThreeStep(prev=s2, logger=logger)
    s4 = StageFourStep(prev=s3, trie=s4_trie, logger=logger)
    s5 = StageFiveStep(prev=s4, logger=logger)
    parse = ParseStep(prev=s5, parser=program_parser)
    resolve = ResolveStep(prev=parse, resolver=resolver)

    return Pipeline(
        {
            StageOne: s1,
            StageTwo: s2,
            StageThree: s3,
            StageFour: s4,
            StageFive: s5,
            ParsedProgram: parse,
            ResolvedProgram: resolve,
        }
    )


class Container(containers.DeclarativeContainer):
    logger = providers.Factory(create_logger)
    s2_trie = providers.Singleton(create_stage_two_trie)
    s4_trie = providers.Singleton(create_stage_four_trie)
    program_parser = providers.Singleton(_create_program_parser)
    resolver = providers.Singleton(StageSeven, logger=logger)

    pipeline = providers.Singleton(
        _create_pipeline,
        s2_trie=s2_trie,
        s4_trie=s4_trie,
        program_parser=program_parser,
        resolver=resolver,
        logger=logger,
    )
