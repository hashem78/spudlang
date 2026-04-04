from spud.core.pipeline import TypeCheckedProgram
from spud.core.string_reader import StringReader
from spud_lsp.container import LspContainer
from spud_lsp.server import SpudLanguageServer


def entrypoint() -> None:
    container: LspContainer = LspContainer()
    pipeline = container.pipeline()

    def parse(text: str) -> TypeCheckedProgram:
        return pipeline.run(StringReader(text))

    server: SpudLanguageServer = SpudLanguageServer(
        parse=parse,
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
