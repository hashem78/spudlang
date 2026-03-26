from pathlib import Path
from typing import Generator


class FileReader:
    def __init__(self, path: Path):
        self._path = path

    def read(self) -> Generator[str, None, None]:
        with open(self._path, "r") as f:
            while char := f.read(1):
                yield char
