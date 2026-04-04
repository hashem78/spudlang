from spud.stage_six import ASTNode, NodeType, Program
from spud_fmt.config import FmtConfig
from spud_fmt.formatter_protocol import NodeFormatter
from spud_fmt.formatters.body_fmt import is_block_node


class Formatter:
    """Dispatches formatting to per-node-type formatters.

    All formatters are injected via the constructor — the DI container
    wires them. Implements ``FormatterDispatch`` so individual formatters
    can recursively format child nodes through this dispatcher.
    """

    def __init__(
        self,
        config: FmtConfig,
        identifier_fmt: NodeFormatter,
        int_fmt: NodeFormatter,
        float_fmt: NodeFormatter,
        string_fmt: NodeFormatter,
        raw_string_fmt: NodeFormatter,
        boolean_fmt: NodeFormatter,
        binary_op_fmt: NodeFormatter,
        function_call_fmt: NodeFormatter,
        binding_fmt: NodeFormatter,
        function_def_fmt: NodeFormatter,
        inline_function_def_fmt: NodeFormatter,
        list_literal_fmt: NodeFormatter,
        if_else_fmt: NodeFormatter,
        for_loop_fmt: NodeFormatter,
        unary_op_fmt: NodeFormatter,
        unit_literal_fmt: NodeFormatter,
    ) -> None:
        self._config = config
        self._registry: dict[NodeType, NodeFormatter] = {
            NodeType.IDENTIFIER: identifier_fmt,
            NodeType.INT_LITERAL: int_fmt,
            NodeType.FLOAT_LITERAL: float_fmt,
            NodeType.STRING_LITERAL: string_fmt,
            NodeType.RAW_STRING_LITERAL: raw_string_fmt,
            NodeType.BOOLEAN_LITERAL: boolean_fmt,
            NodeType.BINARY_OP: binary_op_fmt,
            NodeType.UNARY_OP: unary_op_fmt,
            NodeType.FUNCTION_CALL: function_call_fmt,
            NodeType.BINDING: binding_fmt,
            NodeType.FUNCTION_DEF: function_def_fmt,
            NodeType.INLINE_FUNCTION_DEF: inline_function_def_fmt,
            NodeType.LIST_LITERAL: list_literal_fmt,
            NodeType.IF_ELSE: if_else_fmt,
            NodeType.FOR_LOOP: for_loop_fmt,
            NodeType.UNIT_LITERAL: unit_literal_fmt,
        }

    def format_node(self, node: ASTNode, depth: int) -> str:
        formatter = self._registry.get(node.node_type)
        if formatter is None:
            return ""
        return formatter.format(node, depth)

    def format_program(self, program: Program) -> str:
        """Format a parsed program into consistently styled source text."""
        lines: list[str] = []
        prev_had_block = False

        for i, node in enumerate(program.body):
            has_block = is_block_node(node)
            if i > 0 and self._config.blank_lines_around_blocks and (has_block or prev_had_block):
                lines.append("")
            lines.append(self.format_node(node, depth=0))
            prev_had_block = has_block

        result = "\n".join(lines)
        if self._config.trailing_newline and result:
            result += "\n"
        return result
