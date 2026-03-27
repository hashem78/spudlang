from dependency_injector import containers, providers

from spud.core.string_reader import StringReader
from spud.di.container import _create_program_parser
from spud.di.logging import create_logger
from spud.di.stage_four_trie import create_stage_four_trie
from spud.di.stage_two_trie import create_stage_two_trie
from spud.stage_five.stage_five import StageFive
from spud.stage_four.stage_four import StageFour
from spud.stage_one.stage_one import StageOne
from spud.stage_six.stage_six import StageSix
from spud.stage_three.stage_three import StageThree
from spud.stage_two.stage_two import StageTwo
from spud_lsp.completion import CompletionHandler
from spud_lsp.diagnostics import DiagnosticsHandler
from spud_lsp.hover import HoverHandler
from spud_lsp.symbols import SymbolsHandler


class LspContainer(containers.DeclarativeContainer):
    logger = providers.Factory(create_logger)

    reader = providers.Factory(StringReader, text="")
    stage_one = providers.Factory(StageOne, handle=reader)
    stage_two_trie = providers.Singleton(create_stage_two_trie)
    stage_two = providers.Factory(StageTwo, stage_one=stage_one, trie=stage_two_trie, logger=logger)
    stage_three = providers.Factory(StageThree, stage_two=stage_two, logger=logger)
    stage_four_trie = providers.Singleton(create_stage_four_trie)
    stage_four = providers.Factory(StageFour, stage_three=stage_three, trie=stage_four_trie, logger=logger)
    stage_five = providers.Factory(StageFive, stage_four=stage_four, logger=logger)

    program_parser = providers.Singleton(_create_program_parser)

    stage_six = providers.Factory(StageSix, stage_five=stage_five, program_parser=program_parser, logger=logger)

    diagnostics_handler = providers.Singleton(DiagnosticsHandler)
    hover_handler = providers.Singleton(HoverHandler)
    completion_handler = providers.Singleton(CompletionHandler)
    symbols_handler = providers.Singleton(SymbolsHandler)
