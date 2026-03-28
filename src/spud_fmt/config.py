from enum import Enum

from pydantic import BaseModel


class QuoteStyle(str, Enum):
    SINGLE = "single"
    DOUBLE = "double"


class FmtConfig(BaseModel):
    indent_size: int = 2
    quote_style: QuoteStyle = QuoteStyle.SINGLE
    blank_lines_around_blocks: bool = True
    spaces_around_operators: bool = True
    spaces_around_walrus: bool = True
    spaces_around_fat_arrow: bool = True
    space_after_comma: bool = True
    trailing_newline: bool = True
    collapse_unary_plus: bool = False
