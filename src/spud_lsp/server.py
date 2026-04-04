from lsprotocol import types
from pygls.lsp.server import LanguageServer

from spud.core.pipeline import TypeCheckedProgram
from spud.stage_six.program import Program
from spud_lsp.completion import CompletionHandler
from spud_lsp.diagnostics import DiagnosticsHandler
from spud_lsp.hover import HoverHandler
from spud_lsp.lsp_types import ParseFn
from spud_lsp.semantic_tokens import LEGEND, SemanticTokensHandler
from spud_lsp.symbols import SymbolsHandler


class SpudLanguageServer(LanguageServer):
    def __init__(
        self,
        parse: ParseFn,
        diagnostics: DiagnosticsHandler,
        hover: HoverHandler,
        completion: CompletionHandler,
        symbols: SymbolsHandler,
        semantic_tokens: SemanticTokensHandler,
    ) -> None:
        super().__init__("spud-lsp", "v0.1")
        self._parse = parse
        self._diagnostics = diagnostics
        self._hover = hover
        self._completion = completion
        self._symbols = symbols
        self._semantic_tokens = semantic_tokens
        self._last_program: dict[str, Program] = {}
        self._last_result: dict[str, TypeCheckedProgram] = {}
        self._register_features()

    def _register_features(self) -> None:
        @self.feature(types.TEXT_DOCUMENT_DID_OPEN)
        def did_open(params: types.DidOpenTextDocumentParams) -> None:
            uri: str = params.text_document.uri
            result: TypeCheckedProgram = self._parse(params.text_document.text)
            self._last_program[uri] = result.program
            self._last_result[uri] = result
            self.text_document_publish_diagnostics(
                types.PublishDiagnosticsParams(
                    uri=uri,
                    diagnostics=self._diagnostics.diagnose(result.program, result.type_check_result.errors),
                )
            )

        @self.feature(types.TEXT_DOCUMENT_DID_CHANGE)
        def did_change(params: types.DidChangeTextDocumentParams) -> None:
            uri: str = params.text_document.uri
            doc = self.workspace.get_text_document(uri)
            result: TypeCheckedProgram = self._parse(doc.source)
            self._last_program[uri] = result.program
            self._last_result[uri] = result
            self.text_document_publish_diagnostics(
                types.PublishDiagnosticsParams(
                    uri=uri,
                    diagnostics=self._diagnostics.diagnose(result.program, result.type_check_result.errors),
                )
            )

        @self.feature(types.TEXT_DOCUMENT_HOVER)
        def hover(params: types.HoverParams) -> types.Hover | None:
            result = self._last_result.get(params.text_document.uri)
            if result is None:
                return None
            return self._hover.hover(
                result.type_check_result.typed_program, params.position.line, params.position.character
            )

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

        @self.feature(
            types.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
            types.SemanticTokensRegistrationOptions(legend=LEGEND, full=True),
        )
        def semantic_tokens_full(params: types.SemanticTokensParams) -> types.SemanticTokens | None:
            result: TypeCheckedProgram | None = self._last_result.get(params.text_document.uri)
            if result is None:
                return None
            return self._semantic_tokens.semantic_tokens(result.resolve_result, result.tokens)
