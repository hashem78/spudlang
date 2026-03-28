# spud

A small programming language with a multi-stage parser pipeline, an LSP server, and a code formatter.

## Language

spud uses indentation-based blocks, `:=` for bindings, and `=>` for function definitions. Every expression produces a value.

```
max := 100

validate := (input) =>
  if input > 0
    'positive'
  elif input < 0
    'negative'
  else
    'zero'

for i in range(max)
  result := validate(i)
  print(result)
```

### Bindings

```
x := 42
name := 'hello'
flag := true
items := [1, 2, 3]
```

### Functions

Block functions have an indented body. Inline functions use a single expression.

```
add := (a, b) =>
  result := a + b
  result

double := (x) => x * 2
noop := () => ()
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
        ├── NUMERIC 1
        └── NUMERIC 2
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
```

All options are optional and fall back to the defaults shown above.

### LSP server

```sh
spud-lsp
```

Communicates over stdio. Point your editor's LSP client at the `spud-lsp` binary.

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

The parser is a six-stage pipeline. Each stage transforms its input and passes it to the next.

1. **Stage one** - Character lexer. Reads raw characters and emits single-character tokens with position data.
2. **Stage two** - Keyword matching. Trie-based pass that groups character tokens into keyword tokens (`if`, `for`, `true`, etc.) with word boundary detection.
3. **Stage three** - Identifier grouping. Merges runs of non-symbol characters into identifier tokens, splitting on whitespace and symbols.
4. **Stage four** - Operator matching. Trie-based pass that recognizes multi-character operators (`:=`, `=>`, `==`, `!=`, `<=`, `>=`, `&&`, `||`).
5. **Stage five** - Indentation. Streaming pass that tracks column depth and emits synthetic `INDENT`/`DEDENT` tokens.
6. **Stage six** - AST. Recursive descent parser producing a typed AST from the token stream. Two-pass design: decompose (structural splitting) then classify (type assignment).

The formatter and LSP server are separate packages (`spud_fmt`, `spud_lsp`) under `src/` that depend on the core `spud` package.

## License

MIT
