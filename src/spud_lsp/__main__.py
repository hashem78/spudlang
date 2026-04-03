from dependency_injector import providers

from spud.core.string_reader import StringReader
from spud.stage_six.program import Program
from spud_lsp.container import LspContainer
from spud_lsp.server import SpudLanguageServer


def entrypoint() -> None:
    container: LspContainer = LspContainer()

    stage_seven = container.stage_seven()

    def parse(text: str) -> Program:
        container.reader.override(providers.Factory(StringReader, text=text))
        program: Program = container.stage_six().parse()
        container.reader.reset_override()
        return stage_seven.resolve(program).program

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
