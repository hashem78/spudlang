from spud.stage_six import FunctionTypeExpr, ListTypeExpr, NamedType, TypedParam, TypeExpression


def format_type(node: TypeExpression) -> str:
    match node:
        case NamedType(name=name):
            return name
        case ListTypeExpr(element=element):
            return f"List[{format_type(element)}]"
        case FunctionTypeExpr(params=params, returns=returns):
            param_strs = ", ".join(format_type(p) for p in params)
            return f"Function[[{param_strs}], {format_type(returns)}]"
        case _:
            return "<unknown>"


def format_typed_params(params: list[TypedParam], separator: str) -> str:
    parts = [f"{p.name.name}: {format_type(p.type_annotation)}" for p in params]
    return separator.join(parts)
