from spud.core.types import BoolType, FloatType, IntType, SpudType, SpudTypeKind

K = SpudTypeKind

BINARY_OP_TYPES: dict[tuple[str, SpudTypeKind, SpudTypeKind], SpudType] = {
    ("+", K.INT, K.INT): IntType(),
    ("-", K.INT, K.INT): IntType(),
    ("*", K.INT, K.INT): IntType(),
    ("/", K.INT, K.INT): IntType(),
    ("%", K.INT, K.INT): IntType(),
    ("+", K.FLOAT, K.FLOAT): FloatType(),
    ("-", K.FLOAT, K.FLOAT): FloatType(),
    ("*", K.FLOAT, K.FLOAT): FloatType(),
    ("/", K.FLOAT, K.FLOAT): FloatType(),
    ("%", K.FLOAT, K.FLOAT): FloatType(),
    ("==", K.INT, K.INT): BoolType(),
    ("!=", K.INT, K.INT): BoolType(),
    ("==", K.FLOAT, K.FLOAT): BoolType(),
    ("!=", K.FLOAT, K.FLOAT): BoolType(),
    ("==", K.STRING, K.STRING): BoolType(),
    ("!=", K.STRING, K.STRING): BoolType(),
    ("==", K.BOOL, K.BOOL): BoolType(),
    ("!=", K.BOOL, K.BOOL): BoolType(),
    ("<", K.INT, K.INT): BoolType(),
    (">", K.INT, K.INT): BoolType(),
    ("<=", K.INT, K.INT): BoolType(),
    (">=", K.INT, K.INT): BoolType(),
    ("<", K.FLOAT, K.FLOAT): BoolType(),
    (">", K.FLOAT, K.FLOAT): BoolType(),
    ("<=", K.FLOAT, K.FLOAT): BoolType(),
    (">=", K.FLOAT, K.FLOAT): BoolType(),
    ("&&", K.BOOL, K.BOOL): BoolType(),
    ("||", K.BOOL, K.BOOL): BoolType(),
}

UNARY_OP_TYPES: dict[tuple[str, SpudTypeKind], SpudType] = {
    ("-", K.INT): IntType(),
    ("+", K.INT): IntType(),
    ("-", K.FLOAT): FloatType(),
    ("+", K.FLOAT): FloatType(),
}
