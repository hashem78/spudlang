from typing import Protocol, TypeVar

from spud.stage_six.parse_error import ParseError
from spud.stage_six.token_stream import TokenStream

T = TypeVar("T", covariant=True)


class IParser(Protocol[T]):
    def parse(self, stream: TokenStream) -> T | ParseError: ...
