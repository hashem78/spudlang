from lsprotocol import types

from spud.core.position import Position
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.binding import Binding
from spud.stage_six.for_loop import ForLoop
from spud.stage_six.function_call import FunctionCall
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.identifier import Identifier
from spud.stage_six.if_else import IfElse
from spud.stage_six.inline_function_def import InlineFunctionDef
from spud.stage_six.program import Program
from spud_lsp.utils import find_node_at


class GotoDefHandler:
    def goto_def(self, program: Program, uri: str, line: int, column: int) -> types.Location | None:
        node = find_node_at(program, line, column)
        if node is None:
            return None

        name: str | None = None
        match node:
            case Identifier(name=n):
                name = n
            case FunctionCall(callee=callee):
                name = callee.name
            case _:
                return None

        def_pos = _find_definition_at(program.body, name, line, column)
        if def_pos is None:
            return None

        return types.Location(
            uri=uri,
            range=types.Range(
                start=types.Position(line=def_pos.line, character=def_pos.column),
                end=types.Position(line=def_pos.line, character=def_pos.column + len(name)),
            ),
        )


def _find_definition_at(body: list[ASTNode], name: str, line: int, column: int) -> Position | None:
    """Search for a definition of *name*, only entering scopes that contain the cursor."""
    for node in body:
        match node:
            case Binding(target=target, value=value):
                if target.name == name:
                    return target.position
                inner = _search_value(value, name, line, column)
                if inner is not None:
                    return inner
            case _:
                inner = _search_value(node, name, line, column)
                if inner is not None:
                    return inner
    return None


def _search_value(node: ASTNode, name: str, line: int, column: int) -> Position | None:
    """Search inside a value node, only entering scopes that contain the cursor."""
    if not _contains_position(node, line, column):
        return None

    match node:
        case FunctionDef(params=params, body=body):
            for p in params:
                if p.name.name == name:
                    return p.name.position
            return _find_definition_at(body, name, line, column)
        case InlineFunctionDef(params=params):
            for p in params:
                if p.name.name == name:
                    return p.name.position
            return None
        case ForLoop(variable=variable, body=body):
            if variable.name == name:
                return variable.position
            return _find_definition_at(body, name, line, column)
        case IfElse(branches=branches, else_body=else_body):
            for branch in branches:
                if _contains_position(branch, line, column):
                    return _find_definition_at(branch.body, name, line, column)
            if else_body:
                for stmt in else_body:
                    if _contains_position(stmt, line, column):
                        return _find_definition_at(else_body, name, line, column)
            return None
    return None


def _contains_position(node: ASTNode, line: int, column: int) -> bool:
    if line < node.position.line or line > node.end.line:
        return False
    if line == node.position.line and column < node.position.column:
        return False
    if line == node.end.line and column > node.end.column:
        return False
    return True
