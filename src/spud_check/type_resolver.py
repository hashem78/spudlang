from spud.core.types import FunctionType, ListType, SpudType, UnitType
from spud.stage_six import FunctionTypeExpr, ListTypeExpr, NamedType, TypeExpression
from spud_check.builtin_types import BUILTIN_TYPES
from spud_check.type_errors import TypeError, UnknownTypeError


def resolve_type(
    type_expr: TypeExpression,
    errors: list[TypeError],
) -> SpudType:
    """Resolve a TypeExpression AST node into a SpudType.

    Looks up named types in BUILTIN_TYPES. Recursively resolves element
    types for list types and parameter/return types for function types.
    Appends UnknownTypeError for unrecognized names.
    """
    match type_expr:
        case NamedType(name=name):
            resolved = BUILTIN_TYPES.get(name)
            if resolved is None:
                errors.append(
                    UnknownTypeError(
                        position=type_expr.position,
                        name=name,
                    )
                )
                return UnitType()
            return resolved
        case ListTypeExpr(element=element):
            return ListType(element=resolve_type(element, errors))
        case FunctionTypeExpr(params=params, returns=returns):
            return FunctionType(
                params=tuple(resolve_type(p, errors) for p in params),
                returns=resolve_type(returns, errors),
            )
        case _:
            return UnitType()
