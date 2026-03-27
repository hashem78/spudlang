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

    await client.start_io(sys.executable, "-m", "spud.lsp")

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

    # Shutdown.
    await client.protocol.send_request_async("shutdown", None)
    client.protocol.notify("exit", None)

    print("\nAll smoke tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
