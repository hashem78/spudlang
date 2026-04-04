from lsprotocol import types

from spud.core.types.function_type import FunctionType
from spud.core.types.list_type import ListType
from spud.core.types.spud_type import SpudType
from spud.stage_eight.typed_nodes.typed_binary_op import TypedBinaryOp
from spud.stage_eight.typed_nodes.typed_binding import TypedBinding
from spud.stage_eight.typed_nodes.typed_condition_branch import TypedConditionBranch
from spud.stage_eight.typed_nodes.typed_for_loop import TypedForLoop
from spud.stage_eight.typed_nodes.typed_function_call import TypedFunctionCall
from spud.stage_eight.typed_nodes.typed_function_def import TypedFunctionDef
from spud.stage_eight.typed_nodes.typed_identifier import TypedIdentifier
from spud.stage_eight.typed_nodes.typed_if_else import TypedIfElse
from spud.stage_eight.typed_nodes.typed_list_literal import TypedListLiteral
from spud.stage_eight.typed_nodes.typed_node import TypedNode
from spud.stage_eight.typed_nodes.typed_program import TypedProgram
from spud.stage_eight.typed_nodes.typed_unary_op import TypedUnaryOp


class HoverHandler:
    def hover(self, typed_program: TypedProgram, line: int, column: int) -> types.Hover | None:
        """Find the typed node at the cursor and return hover information with type."""
        node = _find_typed_node_at(typed_program, line, column)
        if node is None:
            return None

        text = _describe(node)
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


def _find_typed_node_at(node: TypedNode, line: int, column: int) -> TypedNode | None:
    if not _in_range(node, line, column):
        return None

    children: list[TypedNode] = _children(node)
    for child in children:
        found = _find_typed_node_at(child, line, column)
        if found is not None:
            return found

    return node


def _in_range(node: TypedNode, line: int, column: int) -> bool:
    if line < node.position.line or line > node.end.line:
        return False
    if line == node.position.line and column < node.position.column:
        return False
    if line == node.end.line and column > node.end.column:
        return False
    return True


def _children(node: TypedNode) -> list[TypedNode]:
    match node:
        case TypedProgram(body=body):
            return list(body)
        case TypedBinding(value=value):
            return [value]
        case TypedFunctionDef(params=params, body=body):
            return [*params, *body]
        case TypedFunctionCall(args=args):
            return list(args)
        case TypedBinaryOp(left=left, right=right):
            return [left, right]
        case TypedUnaryOp(operand=operand):
            return [operand]
        case TypedConditionBranch(condition=condition, body=body):
            return [condition, *body]
        case TypedIfElse(branches=branches, else_body=else_body):
            return [*branches, *(else_body or [])]
        case TypedForLoop(iterable=iterable, body=body):
            return [iterable, *body]
        case TypedListLiteral(elements=elements):
            return list(elements)
        case _:
            return []


def _describe(node: TypedNode) -> str | None:
    type_str = _format_spud_type(node.resolved_type)
    match node:
        case TypedIdentifier(name=name):
            return f"`{name}`: **{type_str}**"
        case TypedBinding(target_name=name):
            return f"`{name}`: **{type_str}**"
        case TypedFunctionCall(callee_name=name):
            return f"`{name}(...)`: **{type_str}**"
        case TypedForLoop(variable_name=name):
            return f"`for {name} in ...`"
        case _:
            return f"**{type_str}**"


def _format_spud_type(t: SpudType) -> str:
    match t:
        case FunctionType(params=params, returns=returns):
            param_strs = ", ".join(_format_spud_type(p) for p in params)
            return f"Function[[{param_strs}], {_format_spud_type(returns)}]"
        case ListType(element=element):
            return f"List[{_format_spud_type(element)}]"
        case _:
            return t.kind.value.capitalize()
