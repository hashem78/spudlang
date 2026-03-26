from typing import Generator, Protocol


class IReader(Protocol):
    def read(self) -> Generator[str, None, None]: ...
