from dependency_injector import containers, providers

from spud.core.file_reader import FileReader
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
from spud_fmt.config import FmtConfig
from spud_fmt.formatter import Formatter
from spud_fmt.formatter_protocol import FormatterDispatch
from spud_fmt.formatters.binary_op_fmt import BinaryOpFormatter
from spud_fmt.formatters.binding_fmt import BindingFormatter
from spud_fmt.formatters.boolean_fmt import BooleanFormatter
from spud_fmt.formatters.for_loop_fmt import ForLoopFormatter
from spud_fmt.formatters.function_call_fmt import FunctionCallFormatter
from spud_fmt.formatters.function_def_fmt import FunctionDefFormatter
from spud_fmt.formatters.identifier_fmt import IdentifierFormatter
from spud_fmt.formatters.if_else_fmt import IfElseFormatter
from spud_fmt.formatters.inline_function_def_fmt import InlineFunctionDefFormatter
from spud_fmt.formatters.list_literal_fmt import ListLiteralFormatter
from spud_fmt.formatters.float_fmt import FloatFormatter
from spud_fmt.formatters.numeric_fmt import NumericFormatter
from spud_fmt.formatters.raw_string_fmt import RawStringFormatter
from spud_fmt.formatters.string_fmt import StringFormatter
from spud_fmt.formatters.unary_op_fmt import UnaryOpFormatter
from spud_fmt.formatters.unit_literal_fmt import UnitLiteralFormatter


def _create_formatter(config: FmtConfig) -> Formatter:
    """Wire formatter dependency graph, resolving the circular dep
    between compound formatters and the dispatcher.

    Same pattern as ``_create_program_parser`` for the parser pipeline:
    create the dispatcher first via ``__new__``, pass a closure to the
    compound formatters so they can call back into it, then ``__init__``
    the dispatcher with all formatters wired.
    """
    formatter = Formatter.__new__(Formatter)

    def fmt_provider() -> FormatterDispatch:
        return formatter

    formatter.__init__(
        config=config,
        identifier_fmt=IdentifierFormatter(),
        numeric_fmt=NumericFormatter(),
        float_fmt=FloatFormatter(config=config),
        string_fmt=StringFormatter(config=config),
        raw_string_fmt=RawStringFormatter(),
        boolean_fmt=BooleanFormatter(),
        binary_op_fmt=BinaryOpFormatter(config=config, fmt=fmt_provider),
        function_call_fmt=FunctionCallFormatter(config=config, fmt=fmt_provider),
        binding_fmt=BindingFormatter(config=config, fmt=fmt_provider),
        function_def_fmt=FunctionDefFormatter(config=config, fmt=fmt_provider),
        inline_function_def_fmt=InlineFunctionDefFormatter(config=config, fmt=fmt_provider),
        list_literal_fmt=ListLiteralFormatter(config=config, fmt=fmt_provider),
        if_else_fmt=IfElseFormatter(config=config, fmt=fmt_provider),
        for_loop_fmt=ForLoopFormatter(config=config, fmt=fmt_provider),
        unary_op_fmt=UnaryOpFormatter(config=config, fmt=fmt_provider),
        unit_literal_fmt=UnitLiteralFormatter(),
    )
    return formatter


class FmtContainer(containers.DeclarativeContainer):
    # Logging
    logger = providers.Factory(create_logger)

    # Parser pipeline
    reader = providers.Factory(FileReader)
    stage_one = providers.Factory(StageOne, handle=reader)
    stage_two_trie = providers.Singleton(create_stage_two_trie)
    stage_two = providers.Factory(StageTwo, stage_one=stage_one, trie=stage_two_trie, logger=logger)
    stage_three = providers.Factory(StageThree, stage_two=stage_two, logger=logger)
    stage_four_trie = providers.Singleton(create_stage_four_trie)
    stage_four = providers.Factory(StageFour, stage_three=stage_three, trie=stage_four_trie, logger=logger)
    stage_five = providers.Factory(StageFive, stage_four=stage_four, logger=logger)
    program_parser = providers.Singleton(_create_program_parser)
    stage_six = providers.Factory(StageSix, stage_five=stage_five, program_parser=program_parser, logger=logger)

    # Config
    config = providers.Singleton(FmtConfig)

    # Formatter (wired via factory to resolve circular dep)
    formatter = providers.Singleton(_create_formatter, config=config)
