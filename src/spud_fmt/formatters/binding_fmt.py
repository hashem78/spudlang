from typing import Callable

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.binding import Binding
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.inline_function_def import InlineFunctionDef
from spud_fmt.config import FmtConfig
from spud_fmt.formatter_protocol import FormatterDispatch
from spud_fmt.formatters.body_fmt import format_body
from spud_fmt.formatters.type_fmt import format_type, format_typed_params


class BindingFormatter:
    def __init__(self, config: FmtConfig, fmt: Callable[[], FormatterDispatch]):
        self._config = config
        self._fmt = fmt

    def format(self, node: ASTNode, depth: int) -> str:
        match node:
            case Binding(target=target, type_annotation=type_ann, value=value):
                indent = " " * (depth * self._config.indent_size)
                type_str = format_type(type_ann)
                walrus = " := " if self._config.spaces_around_walrus else ":="

                match value:
                    case FunctionDef(params=params, return_type=return_type, body=body):
                        separator = ", " if self._config.space_after_comma else ","
                        param_str = format_typed_params(params, separator)
                        ret_str = format_type(return_type)
                        arrow = " =>" if self._config.spaces_around_fat_arrow else "=>"
                        header = f"{indent}{target.name} : {type_str}{walrus}({param_str}) : {ret_str}{arrow}"
                        body_lines = format_body(body, depth + 1, self._config, self._fmt)
                        return f"{header}\n{body_lines}"
                    case InlineFunctionDef():
                        formatted_value = self._fmt().format_node(value, depth)
                        return f"{indent}{target.name} : {type_str}{walrus}{formatted_value}"
                    case _:
                        formatted_value = self._fmt().format_node(value, depth)
                        return f"{indent}{target.name} : {type_str}{walrus}{formatted_value}"
