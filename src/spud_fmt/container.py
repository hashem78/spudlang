from dependency_injector import containers, providers

from spud.di.container import Container as CoreContainer
from spud_fmt.config import FmtConfig
from spud_fmt.formatter import Formatter
from spud_fmt.formatter_protocol import FormatterDispatch
from spud_fmt.formatters.binary_op_fmt import BinaryOpFormatter
from spud_fmt.formatters.binding_fmt import BindingFormatter
from spud_fmt.formatters.boolean_fmt import BooleanFormatter
from spud_fmt.formatters.float_fmt import FloatFormatter
from spud_fmt.formatters.for_loop_fmt import ForLoopFormatter
from spud_fmt.formatters.function_call_fmt import FunctionCallFormatter
from spud_fmt.formatters.function_def_fmt import FunctionDefFormatter
from spud_fmt.formatters.identifier_fmt import IdentifierFormatter
from spud_fmt.formatters.if_else_fmt import IfElseFormatter
from spud_fmt.formatters.inline_function_def_fmt import InlineFunctionDefFormatter
from spud_fmt.formatters.int_fmt import IntFormatter
from spud_fmt.formatters.list_literal_fmt import ListLiteralFormatter
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
        int_fmt=IntFormatter(),
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
    core = providers.Container(CoreContainer)

    pipeline = core.pipeline

    config = providers.Singleton(FmtConfig)
    formatter = providers.Singleton(_create_formatter, config=config)
