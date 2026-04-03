# spud

A small programming language with a multi-stage parser pipeline, scope resolution, an LSP server with semantic highlighting, and a code formatter.

## Language

spud uses indentation-based blocks, `:=` for bindings, and `=>` for function definitions. Every expression produces a value.

```
pi := 3.14159
radius := 5
area := pi * radius * radius

greet := (name) => 'hello ' + name

factorial := (n) =>
  if n == 0
    1
  else
    n * factorial(n - 1)

result := factorial(10)
numbers := [1, 2, 3, 4, 5]

for item in numbers
  doubled := item * 2
  greet('world')

max := (a, b) =>
  if a > b
    a
  else
    b

biggest := max(42, 17)

compose := (f, g) =>
  (x) => f(g(x))
```

### Literals

```
x := 42
pi := 3.14
half := .5
name := 'hello'
raw := `raw string`
flag := true
items := [1, 2, 3]
nothing := ()
```

### Bindings

All bindings are immutable. Rebinding and shadowing are not allowed.

```
x := 42
name := 'hello'
```

### Functions

Block functions have an indented body. Inline functions use a single expression. Self-recursion is supported.

```
add := (a, b) =>
  result := a + b
  result

double := (x) => x * 2
noop := () => ()

factorial := (n) =>
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

for i in range(10)
  print(i)
```

### Expressions

Binary operators with standard precedence, unary minus/plus, function calls, lists, and parenthesized grouping.

```
a + b * c
-x
f(1, 2)
[1, max(3, 4), (x) => x + 1]
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
hatch run build:binary       # spud
hatch run build:lsp-binary   # spud-lsp
hatch run build:fmt-binary   # spud-fmt
```

## Usage

### Parser

Parse a file and print the AST:

```sh
spud program.spud --tree
```

Parse from stdin:

```sh
echo 'x := 1 + 2' | spud /dev/stdin --tree
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
  result
  numbers
  max
  biggest
  compose
  scope
    name
  scope
    n
    scope
    scope
  scope
    item
    doubled
  scope
    a
    b
    scope
    scope
  scope
    f
    g
    scope
      x
```

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
echo 'x:=1+2' | spud-fmt
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

- **Diagnostics** - parse errors and scope resolution errors (undefined variables, duplicate bindings, shadowed names)
- **Semantic highlighting** - functions, parameters, variables, keywords, operators, numbers, and strings each get distinct colors
- **Hover** - shows type information for identifiers, literals, and operators
- **Completion** - keywords and in-scope bindings
- **Document symbols** - top-level bindings

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

The parser is a seven-stage pipeline. Each stage transforms its input and passes it to the next.

1. **Stage one** - Character lexer. Reads raw characters and emits single-character tokens with position data.
2. **Stage two** - Keyword matching. Trie-based pass that groups character tokens into keyword tokens (`if`, `for`, `true`, etc.) with word boundary detection.
3. **Stage three** - Identifier and numeric grouping. Merges runs of non-symbol characters into identifier or integer tokens, splitting on whitespace and symbols.
4. **Stage four** - Operator and float matching. Trie-based pass that recognizes multi-character operators (`:=`, `=>`, `==`, `!=`, `<=`, `>=`, `&&`, `||`). A streaming combiner merges adjacent `INT DOT INT` patterns into float tokens.
5. **Stage five** - Indentation. Streaming pass that tracks column depth and emits synthetic `INDENT`/`DEDENT` tokens.
6. **Stage six** - AST. Recursive descent parser producing a typed AST from the token stream.
7. **Stage seven** - Scope resolution. Walks the AST with an immutable environment tree, validating bindings and references. Reports undefined variables, duplicate bindings, and shadowed names.

The `Environment` in `spud.core` is generic and reusable — stage seven uses `Environment[ASTNode]`, and a future type-checker could use `Environment[Type]` over the same tree structure.

The formatter and LSP server are separate packages (`spud_fmt`, `spud_lsp`) under `src/` that depend on the core `spud` package.

## License

MIT
