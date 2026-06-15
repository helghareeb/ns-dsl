# Grammar & ANTLR toolchain

- `JSON.g4` — Parr's JSON grammar (2020 chapter, Listing 2.4). The DSL grammar for both
  microservice event logs and JSON business rules.
- `antlr-4.13.2-complete.jar` — **pinned** ANTLR tool, version-locked to the
  `antlr4-python3-runtime==4.13.2` pin in `pyproject.toml`. Mismatched tool/runtime versions
  silently break parsing, so both are fixed at 4.13.2.

## Regenerating the parser

The generated parser is **committed** under `src/nsdsl/dsl/generated/`, so running tests and
reproducing results needs no Java. Regenerate only when `JSON.g4` changes:

```bash
make antlr-gen      # needs a JRE (Java 21 is fine); emits flat output into generated/
```

This produces `JSONLexer.py`, `JSONParser.py`, `JSONListener.py`, `JSONVisitor.py` plus
`.tokens`/`.interp` artifacts. CI asserts that regeneration yields no diff against the committed
files.
