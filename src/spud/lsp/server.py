from lsprotocol import types
from pygls.lsp.server import LanguageServer

from spud.lsp.completion import CompletionHandler
from spud.lsp.diagnostics import DiagnosticsHandler
from spud.lsp.hover import HoverHandler
from spud.lsp.symbols import SymbolsHandler
from spud.lsp.lsp_types import ParseFn, ParseResult
from spud.stage_six.program import Program


class SpudLanguageServer(LanguageServer):
    def __init__(
        self,
        parse: ParseFn,
        diagnostics: DiagnosticsHandler,
        hover: HoverHandler,
        completion: CompletionHandler,
        symbols: SymbolsHandler,
    ) -> None:
        super().__init__("spud-lsp", "v0.1")
        self._parse = parse
        self._diagnostics = diagnostics
        self._hover = hover
        self._completion = completion
        self._symbols = symbols
        self._last_program: dict[str, Program] = {}
        self._register_features()

    def _register_features(self) -> None:
        @self.feature(types.TEXT_DOCUMENT_DID_OPEN)
        def did_open(params: types.DidOpenTextDocumentParams) -> None:
            uri: str = params.text_document.uri
            result: ParseResult = self._parse(params.text_document.text)
            if isinstance(result, Program):
                self._last_program[uri] = result
            self.text_document_publish_diagnostics(
                types.PublishDiagnosticsParams(uri=uri, diagnostics=self._diagnostics.diagnose(result))
            )

        @self.feature(types.TEXT_DOCUMENT_DID_CHANGE)
        def did_change(params: types.DidChangeTextDocumentParams) -> None:
            uri: str = params.text_document.uri
            result: ParseResult = self._parse(params.content_changes[-1].text)
            if isinstance(result, Program):
                self._last_program[uri] = result
            self.text_document_publish_diagnostics(
                types.PublishDiagnosticsParams(uri=uri, diagnostics=self._diagnostics.diagnose(result))
            )

        @self.feature(types.TEXT_DOCUMENT_HOVER)
        def hover(params: types.HoverParams) -> types.Hover | None:
            program: Program | None = self._last_program.get(params.text_document.uri)
            if program is None:
                return None
            return self._hover.hover(program, params.position.line, params.position.character)

        @self.feature(
            types.TEXT_DOCUMENT_COMPLETION,
            types.CompletionOptions(trigger_characters=[":"]),
        )
        def completion(params: types.CompletionParams) -> types.CompletionList:
            return self._completion.complete(self._last_program.get(params.text_document.uri))

        @self.feature(types.TEXT_DOCUMENT_DOCUMENT_SYMBOL)
        def document_symbol(params: types.DocumentSymbolParams) -> list[types.SymbolInformation]:
            program: Program | None = self._last_program.get(params.text_document.uri)
            if program is None:
                return []
            return self._symbols.symbols(program, params.text_document.uri)
