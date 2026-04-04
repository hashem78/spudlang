# spud

A small statically-typed programming language with a multi-stage parser pipeline, scope resolution, a type checker, an LSP server with semantic highlighting, and a code formatter.

## Language

spud uses indentation-based blocks, `:=` for bindings, and `=>` for function definitions. Every binding and every function parameter carries a type annotation. Every expression produces a value.

```
pi: Float := 3.14159
radius: Float := 5.0
area: Float := pi * radius * radius

greet: Function[[String], String] := (name: String): String =>
  'hello ' + name

factorial: Function[[Int], Int] := (n: Int): Int =>
  if n == 0
    1
  else
    n * factorial(n - 1)

result: Int := factorial(10)
numbers: List[Int] := [1, 2, 3, 4, 5]

for item: Int in numbers
  doubled: Int := item * 2

max: Function[[Int, Int], Int] := (a: Int, b: Int): Int =>
  if a > b
    a
  else
    b

biggest: Int := max(42, 17)
```

### Types

Built-in types: `Int`, `Float`, `String`, `Bool`, `Unit`.

Compound types:

- `List[T]` — homogeneous lists.
- `Function[[T1, T2, ...], R]` — functions taking `T1, T2, ...` and returning `R`.

### Literals

```
x: Int := 42
pi: Float := 3.14
half: Float := 0.5
name: String := 'hello'
raw: String := `raw string`
flag: Bool := true
items: List[Int] := [1, 2, 3]
nothing: Unit := ()
```

### Bindings

All bindings are immutable and require a type annotation. Rebinding and shadowing are not allowed.

```
x: Int := 42
name: String := 'hello'
```

### Functions

Parameters and return types are annotated. Block functions have an indented body; inline functions use a single expression. Self-recursion is supported.

```
add: Function[[Int, Int], Int] := (a: Int, b: Int): Int =>
  result: Int := a + b
  result

double: Function[[Int], Int] := (x: Int): Int => x * 2
noop: Function[[], Unit] := (): Unit => ()

factorial: Function[[Int], Int] := (n: Int): Int =>
  if n == 0
    1
  else
    n * factorial(n - 1)
```

### Control flow

```
if x > 0
  'positive'
elif x == 0
  'zero'
else
  'negative'

for i: Int in numbers
  doubled: Int := i * 2
```

### Expressions

Binary operators with standard precedence, unary minus/plus, function calls, lists, and parenthesized grouping.

```
a + b * c
-x
f(1, 2)
[1, max(3, 4)]
(a + b) * c
```

## Installation

Requires Python 3.12+ and [hatch](https://hatch.pypa.io/).

```sh
git clone https://github.com/hashem78/spud.git
cd spud
```

To run directly through hatch without building:

```sh
hatch run spud program.spud
```

### Building standalone binaries

Builds self-contained executables using Nuitka and copies them to `~/.local/bin/`:

```sh
hatch run build:all
```

Or build individual tools:

```sh
hatch run build:binary        # spud
hatch run build:lsp-binary    # spud-lsp
hatch run build:fmt-binary    # spud-fmt
hatch run build:check-binary  # spud-check
```

## Usage

### Parser

Parse a file and print the AST:

```sh
spud program.spud --tree
```

Parse from stdin:

```sh
echo 'x: Int := 1 + 2' | spud /dev/stdin --tree
```

Example output:

```
└── BINDING x
    └── BINARY_OP +
        ├── INT 1
        └── INT 2
```

### Scope resolution

Print the resolved environment tree:

```sh
spud program.spud --env
```

Example output:

```
global
  pi
  radius
  area
  greet
  factorial
  scope
    name
  scope
    n
    scope
    scope
```

### Type checker

Run type checking over a file and report type errors:

```sh
spud-check program.spud
```

Reports operator type mismatches, argument count/type mismatches, unknown types, branch type mismatches in `if`/`elif`/`else`, heterogeneous list elements, non-iterable `for` targets, non-callable call targets, and return type mismatches.

### Formatter

Format a file and print to stdout:

```sh
spud-fmt program.spud
```

Format in place:

```sh
spud-fmt program.spud --write
```

Format from stdin:

```sh
echo 'x:Int:=1+2' | spud-fmt
```

#### Configuration

Place a `.spudfmt.yaml` file in your project directory. The formatter searches upward from the input file.

```yaml
indent_size: 2
quote_style: single     # single | double
blank_lines_around_blocks: true
spaces_around_operators: true
spaces_around_walrus: true
spaces_around_fat_arrow: true
space_after_comma: true
trailing_newline: true
collapse_unary_plus: false
normalize_leading_zero: true    # .5 → 0.5
normalize_trailing_zero: true   # 3. → 3.0
```

All options are optional and fall back to the defaults shown above.

### LSP server

```sh
spud-lsp
```

Communicates over stdio. Point your editor's LSP client at the `spud-lsp` binary.

Features:

- **Diagnostics** — parse errors, scope resolution errors (undefined variables, duplicate bindings, shadowed names), and type errors from the type checker.
- **Semantic highlighting** — functions, parameters, variables, keywords, operators, type annotations, numbers, and strings each get distinct colors.
- **Hover** — shows the resolved type for identifiers, literals, operators, and expressions.
- **Go-to-definition** — jump from an identifier reference to its binding or parameter.
- **Completion** — keywords and in-scope bindings.
- **Document symbols** — top-level bindings.

#### Neovim

Register `.spud` as a filetype in `filetype.lua`:

```lua
vim.filetype.add({
  extension = {
    spud = "spud",
  },
})
```

Add the LSP server config in `lsp/spud.lua`:

```lua
return {
  cmd = { "spud-lsp" },
  filetypes = { "spud" },
  root_markers = { "pyproject.toml", ".git" },
}
```

Then enable it in your LSP setup:

```lua
vim.lsp.enable("spud")
```

For format-on-save with [conform.nvim](https://github.com/stevearc/conform.nvim), register the formatter and map it to the `spud` filetype:

```lua
require("conform").setup({
  formatters = {
    spud_fmt = {
      command = "spud-fmt",
    },
  },
  formatters_by_ft = {
    spud = { "spud_fmt" },
  },
})
```

## Testing

Run the full test suite (unit tests, fuzz tests, and golden tests):

```sh
hatch run dev:test
```

Run LSP smoke tests separately:

```sh
hatch run dev:test-lsp
```

### Linting and formatting

```sh
hatch run dev:lint
hatch run dev:fmt
hatch run dev:fmt-check
```

### Type checking

```sh
hatch run dev:typecheck
```

## Architecture

The frontend is an eight-stage pipeline. Each stage transforms its input and passes it to the next. There is no code generation — spud stops after producing a typed AST.

1. **Stage one** — Character lexer. Reads raw characters and emits single-character tokens with position data.
2. **Stage two** — Keyword matching. Trie-based pass that groups character tokens into keyword tokens (`if`, `for`, `true`, etc.) with word boundary detection.
3. **Stage three** — Identifier and numeric grouping. Merges runs of non-symbol characters into identifier or integer tokens, splitting on whitespace and symbols.
4. **Stage four** — Operator and float matching. Trie-based pass that recognizes multi-character operators (`:=`, `=>`, `==`, `!=`, `<=`, `>=`, `&&`, `||`). A streaming combiner merges adjacent `INT DOT INT` patterns into float tokens.
5. **Stage five** — Indentation. Streaming pass that tracks column depth and emits synthetic `INDENT`/`DEDENT` tokens.
6. **Stage six** — AST. Recursive descent parser producing a typed AST from the token stream.
7. **Stage seven** — Scope resolution. Walks the AST with an immutable environment tree, validating bindings and references. Reports undefined variables, duplicate bindings, and shadowed names.
8. **Stage eight** — Type checking. Walks the resolved AST with an `Environment[SpudType]`, resolving type annotations and producing a parallel typed AST alongside any type errors.

The `Environment` in `spud.core` is generic and reusable — stage seven uses `Environment[ASTNode]` for scope resolution, stage eight uses `Environment[SpudType]` for type checking, both over the same tree structure.

Stages one through seven live in the core `spud` package. The type checker (`spud_check`), formatter (`spud_fmt`), and LSP server (`spud_lsp`) are separate top-level packages under `src/` that depend on `spud`.

## License

MIT
