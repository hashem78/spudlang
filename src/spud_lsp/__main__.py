from dependency_injector import providers

from spud.core.string_reader import StringReader
from spud.stage_six.token_stream import TokenStream
from spud_lsp.container import LspContainer
from spud_lsp.lsp_types import ParseResult
from spud_lsp.server import SpudLanguageServer


def entrypoint() -> None:
    container: LspContainer = LspContainer()
    stage_seven = container.stage_seven()

    def parse(text: str) -> ParseResult:
        container.reader.override(providers.Factory(StringReader, text=text))
        tokens = list(container.stage_five().parse())
        stream = TokenStream(tokens)
        program = container.program_parser().parse(stream)
        container.reader.reset_override()
        resolve_result = stage_seven.resolve(program)
        return ParseResult(resolve_result=resolve_result, tokens=tokens)

    server: SpudLanguageServer = SpudLanguageServer(
        parse=parse,
        diagnostics=container.diagnostics_handler(),
        hover=container.hover_handler(),
        completion=container.completion_handler(),
        symbols=container.symbols_handler(),
        semantic_tokens=container.semantic_tokens_handler(),
    )
    server.start_io()


if __name__ == "__main__":
    entrypoint()
