from lsprotocol import types

from spud.stage_six.binding import Binding
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.program import Program

_KEYWORD_COMPLETIONS: list[types.CompletionItem] = [
    types.CompletionItem(label="if", kind=types.CompletionItemKind.Keyword),
    types.CompletionItem(label="elif", kind=types.CompletionItemKind.Keyword),
    types.CompletionItem(label="else", kind=types.CompletionItemKind.Keyword),
    types.CompletionItem(label="for", kind=types.CompletionItemKind.Keyword),
    types.CompletionItem(label="in", kind=types.CompletionItemKind.Keyword),
    types.CompletionItem(label="true", kind=types.CompletionItemKind.Keyword),
    types.CompletionItem(label="false", kind=types.CompletionItemKind.Keyword),
    types.CompletionItem(label=":=", kind=types.CompletionItemKind.Operator),
    types.CompletionItem(label="=>", kind=types.CompletionItemKind.Operator),
]


class CompletionHandler:
    def complete(self, program: Program | None) -> types.CompletionList:
        """Return keyword completions and in-scope identifiers."""
        items: list[types.CompletionItem] = list(_KEYWORD_COMPLETIONS)

        if program is not None:
            for stmt in program.body:
                if isinstance(stmt, Binding):
                    kind: types.CompletionItemKind = (
                        types.CompletionItemKind.Function
                        if isinstance(stmt.value, FunctionDef)
                        else types.CompletionItemKind.Variable
                    )
                    items.append(types.CompletionItem(label=stmt.target.name, kind=kind))

        return types.CompletionList(is_incomplete=False, items=items)
