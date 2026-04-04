from spud.stage_six.ast_node import ASTNode
from spud.stage_six.binary_op import BinaryOp
from spud.stage_six.binding import Binding
from spud.stage_six.boolean_literal import BooleanLiteral
from spud.stage_six.condition_branch import ConditionBranch
from spud.stage_six.float_literal import FloatLiteral
from spud.stage_six.for_loop import ForLoop
from spud.stage_six.function_call import FunctionCall
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.identifier import Identifier
from spud.stage_six.if_else import IfElse
from spud.stage_six.inline_function_def import InlineFunctionDef
from spud.stage_six.int_literal import IntLiteral
from spud.stage_six.list_literal import ListLiteral
from spud.stage_six.program import Program
from spud.stage_six.raw_string_literal import RawStringLiteral
from spud.stage_six.string_literal import StringLiteral
from spud.stage_six.unary_op import UnaryOp
from spud.stage_six.unit_literal import UnitLiteral


def print_ast(program: Program) -> None:
    for i, node in enumerate(program.body):
        is_last = i == len(program.body) - 1
        _print_node(node, prefix="", is_last=is_last)


def _print_node(node: ASTNode, prefix: str, is_last: bool) -> None:
    connector = "└── " if is_last else "├── "
    child_prefix = prefix + ("    " if is_last else "│   ")
    label = _label(node)
    print(f"{prefix}{connector}{label}")

    children = _children(node)
    for i, child in enumerate(children):
        _print_node(child, child_prefix, is_last=i == len(children) - 1)


def _label(node: ASTNode) -> str:
    match node:
        case Identifier(name=name):
            return f"IDENTIFIER {name}"
        case IntLiteral(value=value):
            return f"INT {value}"
        case FloatLiteral(value=value):
            return f"FLOAT {value}"
        case StringLiteral(value=value):
            return f"STRING {value}"
        case RawStringLiteral(value=value):
            return f"RAW_STRING {value}"
        case BooleanLiteral(value=value):
            return f"BOOLEAN {value}"
        case Binding(target=target):
            return f"BINDING {target.name}"
        case InlineFunctionDef(params=params):
            names = ", ".join(p.name.name for p in params)
            return f"INLINE_FUNCTION_DEF ({names})"
        case FunctionDef(params=params):
            names = ", ".join(p.name.name for p in params)
            return f"FUNCTION_DEF ({names})"
        case FunctionCall(callee=callee):
            return f"CALL {callee.name}"
        case BinaryOp(operator=op):
            return f"BINARY_OP {op}"
        case UnaryOp(operator=op):
            return f"UNARY_OP {op}"
        case ListLiteral(elements=elements):
            return f"LIST [{len(elements)}]"
        case UnitLiteral():
            return "UNIT"
        case ConditionBranch():
            return "BRANCH"
        case IfElse():
            return "IF_ELSE"
        case ForLoop(variable=var):
            return f"FOR {var.name}"
        case _:
            return node.node_type.value


def _children(node: ASTNode) -> list[ASTNode]:
    match node:
        case Binding(value=value):
            return [value]
        case ListLiteral(elements=elements):
            return list(elements)
        case InlineFunctionDef(body=body):
            return [body]
        case FunctionDef(body=body):
            return list(body)
        case FunctionCall(args=args):
            return list(args)
        case BinaryOp(left=left, right=right):
            return [left, right]
        case UnaryOp(operand=operand):
            return [operand]
        case ConditionBranch(condition=condition, body=body):
            return [condition, *body]
        case IfElse(branches=branches, else_body=else_body):
            children: list[ASTNode] = list(branches)
            if else_body:
                children.extend(else_body)
            return children
        case ForLoop(iterable=iterable, body=body):
            return [iterable, *body]
        case _:
            return []
