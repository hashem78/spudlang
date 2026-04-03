from dependency_injector import containers, providers

from spud.di.container import Container as CoreContainer
from spud_lsp.completion import CompletionHandler
from spud_lsp.diagnostics import DiagnosticsHandler
from spud_lsp.hover import HoverHandler
from spud_lsp.semantic_tokens import SemanticTokensHandler
from spud_lsp.symbols import SymbolsHandler


class LspContainer(containers.DeclarativeContainer):
    core = providers.Container(CoreContainer)

    pipeline = core.pipeline

    diagnostics_handler = providers.Singleton(DiagnosticsHandler)
    semantic_tokens_handler = providers.Singleton(SemanticTokensHandler)
    hover_handler = providers.Singleton(HoverHandler)
    completion_handler = providers.Singleton(CompletionHandler)
    symbols_handler = providers.Singleton(SymbolsHandler)
