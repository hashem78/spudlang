from lsprotocol import types

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.binary_op import BinaryOp
from spud.stage_six.binding import Binding
from spud.stage_six.boolean_literal import BooleanLiteral
from spud.stage_six.for_loop import ForLoop
from spud.stage_six.function_call import FunctionCall
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.identifier import Identifier
from spud.stage_six.if_else import IfElse
from spud.stage_six.numeric_literal import NumericLiteral
from spud.stage_six.program import Program
from spud.stage_six.raw_string_literal import RawStringLiteral
from spud.stage_six.string_literal import StringLiteral
from spud_lsp.utils import find_node_at


class HoverHandler:
    def hover(self, program: Program, line: int, column: int) -> types.Hover | None:
        """Find the node at the cursor and return hover information."""
        node: ASTNode | None = find_node_at(program, line, column)
        if node is None:
            return None

        text: str | None = _describe(node)
        if text is None:
            return None

        return types.Hover(
            contents=types.MarkupContent(
                kind=types.MarkupKind.Markdown,
                value=text,
            ),
            range=types.Range(
                start=types.Position(line=node.position.line, character=node.position.column),
                end=types.Position(line=node.end.line, character=node.end.column),
            ),
        )


def _describe(node: ASTNode) -> str | None:
    match node:
        case Identifier(name=name):
            return f"**Identifier** `{name}`"
        case NumericLiteral(value=value):
            return f"**Numeric literal** `{value}`"
        case StringLiteral(value=value):
            return f"**String literal** `{value}`"
        case RawStringLiteral(value=value):
            return f"**Raw string literal** `{value}`"
        case BooleanLiteral(value=value):
            return f"**Boolean literal** `{value}`"
        case Binding(target=target):
            return f"**Binding** `{target.name}`"
        case FunctionDef(params=params):
            names: str = ", ".join(p.name for p in params)
            return f"**Function** `({names}) =>`"
        case FunctionCall(callee=callee):
            return f"**Function call** `{callee.name}(...)`"
        case BinaryOp(operator=op):
            return f"**Binary operation** `{op}`"
        case IfElse():
            return "**If/else expression**"
        case ForLoop(variable=var):
            return f"**For loop** `for {var.name} in ...`"
        case _:
            return None
