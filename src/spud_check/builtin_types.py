from spud.core.types import BoolType, FloatType, IntType, SpudType, StringType, UnitType

BUILTIN_TYPES: dict[str, SpudType] = {
    "Int": IntType(),
    "Float": FloatType(),
    "String": StringType(),
    "Bool": BoolType(),
    "Unit": UnitType(),
}
