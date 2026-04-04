from spud.core import Position
from spud.stage_six import (
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
    NamedType,
    Program,
    RawStringLiteral,
    StringLiteral,
    TypedParam,
    TypeExpression,
    UnaryOp,
    UnitLiteral,
)
from spud_fmt import FmtConfig, Formatter
from spud_fmt.container import _create_formatter

P = Position(line=0, column=0)


def fmt(config: FmtConfig | None = None) -> Formatter:
    return _create_formatter(config or FmtConfig())


def id(name: str) -> Identifier:
    return Identifier(position=P, end=P, name=name)


def num(value: int) -> IntLiteral:
    return IntLiteral(position=P, end=P, value=value)


def float_(value: float) -> FloatLiteral:
    return FloatLiteral(position=P, end=P, value=value)


def str_(value: str) -> StringLiteral:
    return StringLiteral(position=P, end=P, value=value)


def raw(value: str) -> RawStringLiteral:
    return RawStringLiteral(position=P, end=P, value=value)


def bool_(value: bool) -> BooleanLiteral:
    return BooleanLiteral(position=P, end=P, value=value)


def binop(left, op: str, right) -> BinaryOp:
    return BinaryOp(position=P, end=P, left=left, operator=op, right=right)


def neg(operand) -> UnaryOp:
    return UnaryOp(position=P, end=P, operator="-", operand=operand)


def pos(operand) -> UnaryOp:
    return UnaryOp(position=P, end=P, operator="+", operand=operand)


def call(name: str, *args) -> FunctionCall:
    return FunctionCall(position=P, end=P, callee=id(name), args=list(args))


def named_type(name: str) -> NamedType:
    return NamedType(position=P, end=P, name=name)


def typed_param(name: str, type_name: str = "Int") -> TypedParam:
    return TypedParam(name=id(name), type_annotation=named_type(type_name))


def bind(name: str, value, type_ann: TypeExpression | None = None) -> Binding:
    return Binding(position=P, end=P, target=id(name), type_annotation=type_ann or named_type("Int"), value=value)


def funcdef(params: list[str], body: list, return_type: TypeExpression | None = None) -> FunctionDef:
    return FunctionDef(
        position=P,
        end=P,
        params=[typed_param(p) for p in params],
        return_type=return_type or named_type("Int"),
        body=body,
    )


def branch(condition, body: list) -> ConditionBranch:
    return ConditionBranch(position=P, end=P, condition=condition, body=body)


def ifelse(branches: list, else_body=None) -> IfElse:
    return IfElse(position=P, end=P, branches=branches, else_body=else_body)


def forloop(var: str, iterable, body: list, var_type: TypeExpression | None = None) -> ForLoop:
    return ForLoop(
        position=P, end=P, variable=id(var), variable_type=var_type or named_type("Int"), iterable=iterable, body=body
    )


def inline_funcdef(params: list[str], body, return_type: TypeExpression | None = None) -> InlineFunctionDef:
    return InlineFunctionDef(
        position=P,
        end=P,
        params=[typed_param(p) for p in params],
        return_type=return_type or named_type("Int"),
        body=body,
    )


def list_(*elements) -> ListLiteral:
    return ListLiteral(position=P, end=P, elements=list(elements))


def unit() -> UnitLiteral:
    return UnitLiteral(position=P, end=P)


def program(*body) -> Program:
    return Program(position=P, end=P, body=list(body))
