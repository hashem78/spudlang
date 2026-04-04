from pydantic import BaseModel


class Position(BaseModel, frozen=True):
    line: int
    column: int
