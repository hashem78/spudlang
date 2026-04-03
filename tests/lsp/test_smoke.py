"""Smoke test for the spud LSP server.

Run manually: hatch run python tests/test_lsp_smoke.py
"""

import asyncio
import sys

from lsprotocol import types
from pygls.client import JsonRPCClient


async def main() -> int:
    client: JsonRPCClient = JsonRPCClient()

    # Capture diagnostics published by the server.
    diagnostics_received: list[types.PublishDiagnosticsParams] = []

    @client.feature(types.TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS)
    def on_diagnostics(params: types.PublishDiagnosticsParams) -> None:
        diagnostics_received.append(params)

    await client.start_io(sys.executable, "-m", "spud_lsp")

    # Initialize.
    init_result: types.InitializeResult = await client.protocol.send_request_async(
        "initialize",
        types.InitializeParams(
            process_id=None,
            root_uri=None,
            capabilities=types.ClientCapabilities(),
        ),
    )
    server_info = getattr(init_result, "serverInfo", None)
    server_name: str = getattr(server_info, "name", "unknown") if server_info else "unknown"
    print(f"Server name: {server_name}")
    client.protocol.notify("initialized", types.InitializedParams())

    # Open a valid document.
    valid_text: str = "x := 5\nadd := (a, b) =>\n  a + b\nadd(1, 2)"
    client.protocol.notify(
        "textDocument/didOpen",
        types.DidOpenTextDocumentParams(
            text_document=types.TextDocumentItem(
                uri="file:///test.spud",
                language_id="spud",
                version=1,
                text=valid_text,
            )
        ),
    )
    await asyncio.sleep(0.5)

    # Check diagnostics — should be empty for valid code.
    valid_diags: list[types.PublishDiagnosticsParams] = [
        d for d in diagnostics_received if d.uri == "file:///test.spud"
    ]
    if valid_diags and valid_diags[-1].diagnostics:
        print(f"FAIL: unexpected diagnostics for valid code: {valid_diags[-1].diagnostics}")
        return 1
    print("OK: no diagnostics for valid code")

    # Request completion.
    completions: types.CompletionList = await client.protocol.send_request_async(
        "textDocument/completion",
        types.CompletionParams(
            text_document=types.TextDocumentIdentifier(uri="file:///test.spud"),
            position=types.Position(line=0, character=0),
        ),
    )
    labels: list[str] = [item.label for item in completions.items]
    print(f"Completions: {labels}")
    if "if" not in labels:
        print("FAIL: 'if' keyword missing from completions")
        return 1
    if "x" not in labels:
        print("FAIL: 'x' binding missing from completions")
        return 1
    if "add" not in labels:
        print("FAIL: 'add' binding missing from completions")
        return 1
    print("OK: completions include keywords and bindings")

    # Request hover.
    hover_result: types.Hover | None = await client.protocol.send_request_async(
        "textDocument/hover",
        types.HoverParams(
            text_document=types.TextDocumentIdentifier(uri="file:///test.spud"),
            position=types.Position(line=0, character=0),
        ),
    )
    if hover_result is None:
        print("FAIL: no hover result at line 0, char 0")
        return 1
    print(f"Hover: {hover_result.contents.value}")
    print("OK: hover returns info")

    # Request document symbols.
    symbols: list[types.SymbolInformation] = await client.protocol.send_request_async(
        "textDocument/documentSymbol",
        types.DocumentSymbolParams(
            text_document=types.TextDocumentIdentifier(uri="file:///test.spud"),
        ),
    )
    symbol_names: list[str] = [s["name"] if isinstance(s, dict) else s.name for s in symbols]
    print(f"Symbols: {symbol_names}")
    if "x" not in symbol_names or "add" not in symbol_names:
        print("FAIL: missing symbols")
        return 1
    print("OK: document symbols include bindings")

    # Open an invalid document — should produce diagnostics.
    diagnostics_received.clear()
    client.protocol.notify(
        "textDocument/didOpen",
        types.DidOpenTextDocumentParams(
            text_document=types.TextDocumentItem(
                uri="file:///bad.spud",
                language_id="spud",
                version=1,
                text=":= broken",
            )
        ),
    )
    await asyncio.sleep(1.0)

    bad_diags = [d for d in diagnostics_received if d.uri == "file:///bad.spud"]
    if not bad_diags or not bad_diags[-1].diagnostics:
        print(f"FAIL: no diagnostics for invalid code (received: {diagnostics_received})")
        return 1
    print(f"Diagnostic: {bad_diags[-1].diagnostics[0].message}")
    print("OK: diagnostics reported for invalid code")

    # Diagnostic cases — verify specific error messages.
    diag_cases: list[tuple[str, str]] = [
        ('"hello', "unterminated string literal"),
        ("'hello", "unterminated string literal"),
        ("`hello", "unterminated raw string literal"),
        ("foo(1, 2", "unterminated '('"),
        ("(a + b", "unterminated '('"),
        ("if true", "in if body"),
        ("for in x", "in for loop variable"),
        ("else\n  x", "'else' without matching 'if'"),
        ("elif true\n  x", "'elif' without matching 'if'"),
        ("x := y + 1", "undefined variable 'y'"),
        ("x := 1\nx := 2", "duplicate binding 'x'"),
        ("x := 1\nf := (x) =>\n  x", "'x' shadows an outer binding"),
    ]

    for i, (code, expected_fragment) in enumerate(diag_cases):
        diagnostics_received.clear()
        test_uri: str = f"file:///diag_case_{i}.spud"
        client.protocol.notify(
            "textDocument/didOpen",
            types.DidOpenTextDocumentParams(
                text_document=types.TextDocumentItem(
                    uri=test_uri,
                    language_id="spud",
                    version=1,
                    text=code,
                )
            ),
        )
        await asyncio.sleep(0.5)

        case_diags = [d for d in diagnostics_received if d.uri == test_uri]
        if not case_diags or not case_diags[-1].diagnostics:
            print(f"FAIL: no diagnostics for {code!r}")
            return 1
        actual_msg: str = case_diags[-1].diagnostics[0].message
        if expected_fragment not in actual_msg:
            print(f"FAIL: {code!r} -> {actual_msg!r}, expected to contain {expected_fragment!r}")
            return 1
        print(f"OK: {code!r} -> {actual_msg}")

    # Multiple errors in one file — verify recovery collects all.
    diagnostics_received.clear()
    multi_error_text: str = "x := 5\n:= broken\ny := 10\n:= also broken"
    client.protocol.notify(
        "textDocument/didOpen",
        types.DidOpenTextDocumentParams(
            text_document=types.TextDocumentItem(
                uri="file:///multi.spud",
                language_id="spud",
                version=1,
                text=multi_error_text,
            )
        ),
    )
    await asyncio.sleep(0.5)

    multi_diags = [d for d in diagnostics_received if d.uri == "file:///multi.spud"]
    if not multi_diags:
        print("FAIL: no diagnostics for multi-error file")
        return 1
    diag_count: int = len(multi_diags[-1].diagnostics)
    if diag_count < 2:
        print(f"FAIL: expected multiple diagnostics, got {diag_count}")
        return 1
    print(f"OK: multi-error file produced {diag_count} diagnostics")

    # Shutdown.
    await client.protocol.send_request_async("shutdown", None)
    client.protocol.notify("exit", None)

    print("\nAll smoke tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
