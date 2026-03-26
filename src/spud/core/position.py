from pydantic import BaseModel


class Position(BaseModel):
    line: int
    column: int
