from spud.core import StringReader
from spud.core.pipeline import ResolvedProgram
from spud_lsp.container import LspContainer
from spud_lsp.server import SpudLanguageServer


def entrypoint() -> None:
    container: LspContainer = LspContainer()
    pipeline = container.pipeline()

    def parse(text: str) -> ResolvedProgram:
        return pipeline.run(StringReader(text))

    server: SpudLanguageServer = SpudLanguageServer(
        parse=parse,
        checker=container.checker(),
        diagnostics=container.diagnostics_handler(),
        hover=container.hover_handler(),
        completion=container.completion_handler(),
        symbols=container.symbols_handler(),
        semantic_tokens=container.semantic_tokens_handler(),
        goto_def=container.goto_def_handler(),
    )
    server.start_io()


if __name__ == "__main__":
    entrypoint()
