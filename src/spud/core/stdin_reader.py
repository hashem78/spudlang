import sys
from typing import Generator


class StdinReader:
    def read(self) -> Generator[str, None, None]:
        for char in sys.stdin.read():
            yield char
