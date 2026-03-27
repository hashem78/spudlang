from dependency_injector import providers

from spud.core.string_reader import StringReader
from spud.lsp.container import LspContainer
from spud.lsp.server import SpudLanguageServer
from spud.lsp.lsp_types import ParseResult


def entrypoint() -> None:
    container: LspContainer = LspContainer()

    def parse(text: str) -> ParseResult:
        container.reader.override(providers.Factory(StringReader, text=text))
        result: ParseResult = container.stage_six().parse()
        container.reader.reset_override()
        return result

    server: SpudLanguageServer = SpudLanguageServer(
        parse=parse,
        diagnostics=container.diagnostics_handler(),
        hover=container.hover_handler(),
        completion=container.completion_handler(),
        symbols=container.symbols_handler(),
    )
    server.start_io()


if __name__ == "__main__":
    entrypoint()
