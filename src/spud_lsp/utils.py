from spud.stage_six.ast_node import ASTNode
from spud.stage_six.binary_op import BinaryOp
from spud.stage_six.binding import Binding
from spud.stage_six.condition_branch import ConditionBranch
from spud.stage_six.for_loop import ForLoop
from spud.stage_six.function_call import FunctionCall
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.if_else import IfElse
from spud.stage_six.program import Program


def find_node_at(node: ASTNode, line: int, column: int) -> ASTNode | None:
    """Walk the AST to find the deepest node containing the given position."""
    if not _in_range(node, line, column):
        return None

    children: list[ASTNode] = []
    match node:
        case Program(body=body):
            children = list(body)
        case Binding(value=value):
            children = [node.target, value]
        case FunctionDef(params=params, body=body):
            children = [*[p.name for p in params], *body]
        case FunctionCall(callee=callee, args=args):
            children = [callee, *args]
        case BinaryOp(left=left, right=right):
            children = [left, right]
        case ConditionBranch(condition=condition, body=body):
            children = [condition, *body]
        case IfElse(branches=branches, else_body=else_body):
            children = [*branches, *(else_body or [])]
        case ForLoop(variable=variable, iterable=iterable, body=body):
            children = [variable, iterable, *body]

    for child in children:
        found = find_node_at(child, line, column)
        if found is not None:
            return found

    return node


def _in_range(node: ASTNode, line: int, column: int) -> bool:
    start = node.position
    end = node.end
    if line < start.line or line > end.line:
        return False
    if line == start.line and column < start.column:
        return False
    if line == end.line and column > end.column:
        return False
    return True
