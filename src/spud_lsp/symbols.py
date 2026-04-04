from lsprotocol import types

from spud.stage_six import Binding, FunctionDef, Program


class SymbolsHandler:
    def symbols(self, program: Program, uri: str) -> list[types.SymbolInformation]:
        """Return document symbols for the outline view."""
        result: list[types.SymbolInformation] = []

        for stmt in program.body:
            if not isinstance(stmt, Binding):
                continue

            kind: types.SymbolKind = (
                types.SymbolKind.Function if isinstance(stmt.value, FunctionDef) else types.SymbolKind.Variable
            )

            result.append(
                types.SymbolInformation(
                    name=stmt.target.name,
                    kind=kind,
                    location=types.Location(
                        uri=uri,
                        range=types.Range(
                            start=types.Position(line=stmt.position.line, character=stmt.position.column),
                            end=types.Position(line=stmt.end.line, character=stmt.end.column),
                        ),
                    ),
                )
            )

        return result
