from spud.stage_six import (
    ASTNode,
    BinaryOp,
    Binding,
    BooleanLiteral,
    ConditionBranch,
    FloatLiteral,
    ForLoop,
    FunctionCall,
    FunctionDef,
    Identifier,
    IfElse,
    InlineFunctionDef,
    IntLiteral,
    ListLiteral,
    Program,
    RawStringLiteral,
    StringLiteral,
    UnaryOp,
    UnitLiteral,
)


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
