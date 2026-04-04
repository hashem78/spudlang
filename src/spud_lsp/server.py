from lsprotocol import types
from pygls.lsp.server import LanguageServer

from spud.core.pipeline import ResolvedProgram
from spud.stage_six.program import Program
from spud_check.type_check_result import TypeCheckResult
from spud_check.type_checker import TypeChecker
from spud_lsp.completion import CompletionHandler
from spud_lsp.diagnostics import DiagnosticsHandler
from spud_lsp.goto_def import GotoDefHandler
from spud_lsp.hover import HoverHandler
from spud_lsp.lsp_types import ParseFn
from spud_lsp.semantic_tokens import LEGEND, SemanticTokensHandler
from spud_lsp.symbols import SymbolsHandler


class SpudLanguageServer(LanguageServer):
    def __init__(
        self,
        parse: ParseFn,
        checker: TypeChecker,
        diagnostics: DiagnosticsHandler,
        hover: HoverHandler,
        completion: CompletionHandler,
        symbols: SymbolsHandler,
        semantic_tokens: SemanticTokensHandler,
        goto_def: GotoDefHandler,
    ) -> None:
        super().__init__("spud-lsp", "v0.1")
        self._parse = parse
        self._checker = checker
        self._diagnostics = diagnostics
        self._hover = hover
        self._completion = completion
        self._symbols = symbols
        self._semantic_tokens = semantic_tokens
        self._goto_def = goto_def
        self._last_program: dict[str, Program] = {}
        self._last_result: dict[str, ResolvedProgram] = {}
        self._last_check: dict[str, TypeCheckResult] = {}
        self._register_features()

    def _register_features(self) -> None:
        @self.feature(types.TEXT_DOCUMENT_DID_OPEN)
        def did_open(params: types.DidOpenTextDocumentParams) -> None:
            uri: str = params.text_document.uri
            result: ResolvedProgram = self._parse(params.text_document.text)
            check_result = self._checker.check(result.program)
            self._last_program[uri] = result.program
            self._last_result[uri] = result
            self._last_check[uri] = check_result
            self.text_document_publish_diagnostics(
                types.PublishDiagnosticsParams(
                    uri=uri,
                    diagnostics=self._diagnostics.diagnose(result.program, check_result.errors),
                )
            )

        @self.feature(types.TEXT_DOCUMENT_DID_CHANGE)
        def did_change(params: types.DidChangeTextDocumentParams) -> None:
            uri: str = params.text_document.uri
            doc = self.workspace.get_text_document(uri)
            result: ResolvedProgram = self._parse(doc.source)
            check_result = self._checker.check(result.program)
            self._last_program[uri] = result.program
            self._last_result[uri] = result
            self._last_check[uri] = check_result
            self.text_document_publish_diagnostics(
                types.PublishDiagnosticsParams(
                    uri=uri,
                    diagnostics=self._diagnostics.diagnose(result.program, check_result.errors),
                )
            )

        @self.feature(types.TEXT_DOCUMENT_HOVER)
        def hover(params: types.HoverParams) -> types.Hover | None:
            check_result = self._last_check.get(params.text_document.uri)
            if check_result is None:
                return None
            return self._hover.hover(check_result.typed_program, params.position.line, params.position.character)

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
            result: ResolvedProgram | None = self._last_result.get(params.text_document.uri)
            if result is None:
                return None
            return self._semantic_tokens.semantic_tokens(result.resolve_result, result.tokens)

        @self.feature(types.TEXT_DOCUMENT_DEFINITION)
        def definition(params: types.DefinitionParams) -> types.Location | None:
            program: Program | None = self._last_program.get(params.text_document.uri)
            if program is None:
                return None
            return self._goto_def.goto_def(
                program, params.text_document.uri, params.position.line, params.position.character
            )
