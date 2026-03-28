from typing import Generator

import structlog

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
from spud.stage_six.program import Program
from spud.stage_six.token_stream import TokenStream
from spud.stage_three.stage_three import StageThree
from spud.stage_two.stage_two import StageTwo


class _StringReader:
    def __init__(self, text: str):
        self._text = text

    def read(self) -> Generator[str, None, None]:
        for char in self._text:
            yield char


def _create_program_parser() -> dict:
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


def parse(text: str) -> Program:
    reader = _StringReader(text)
    s1 = StageOne(reader)
    s2 = StageTwo(s1, create_stage_two_trie(), structlog.get_logger())
    s3 = StageThree(s2, structlog.get_logger())
    s4 = StageFour(s3, create_stage_four_trie(), structlog.get_logger())
    s5 = StageFive(s4, structlog.get_logger())
    tokens = list(s5.parse())
    stream = TokenStream(tokens)
    parsers = _create_program_parser()
    return parsers["program_parser"].parse(stream)
