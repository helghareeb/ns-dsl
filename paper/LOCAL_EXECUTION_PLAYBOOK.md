# LOCAL_EXECUTION_PLAYBOOK — validated commands

All commands run from the project root. A local `.venv` (Python 3.13) is used.

## One-time setup
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'      # core + dev (pytest, hypothesis, matplotlib)
# For the Docker testbed later (M5):
# .venv/bin/python -m pip install -e '.[testbed]'  # fastapi, uvicorn, httpx, redis, docker
```

## Validated commands (expected result)
| Command | Expect |
|---------|--------|
| `.venv/bin/python -m pytest -q tests/` | 40 passed (as of M4) |
| `.venv/bin/python -c "import nsdsl; print(nsdsl.__version__)"` | `0.1.0` |
| `make antlr-gen` | regenerates `src/nsdsl/dsl/generated/JSON*.py` (needs Java; jar pinned in `grammar/`) |

Note: `make test` uses `PYTHONPATH=src:.`. When calling pytest directly, `pyproject.toml`
already sets `pythonpath = ["src", "."]`, so `nsdsl` and `services` both import.

## Tooling versions (pinned)
- Python 3.13 (requires-python >=3.10)
- ANTLR tool + runtime: 4.13.2 (jar in `grammar/`, runtime in `pyproject.toml`)
- Java 21 (only needed for `make antlr-gen`)

## Not yet wired (future milestones)
- `make experiments` / `make figures` / `make tables` — exist as Makefile targets but the
  scripts (`experiments/run_all.py`, `analyze_results.py`, ...) are not written until M9.
- `make up` / `make down` — Docker testbed, not built until M5.
