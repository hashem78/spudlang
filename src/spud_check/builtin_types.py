from spud.core.types.bool_type import BoolType
from spud.core.types.float_type import FloatType
from spud.core.types.int_type import IntType
from spud.core.types.spud_type import SpudType
from spud.core.types.string_type import StringType
from spud.core.types.unit_type import UnitType

BUILTIN_TYPES: dict[str, SpudType] = {
    "Int": IntType(),
    "Float": FloatType(),
    "String": StringType(),
    "Bool": BoolType(),
    "Unit": UnitType(),
}
