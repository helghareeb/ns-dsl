# ns-dsl — research-software build for the FGCS extended paper.
# Run everything from the project root. Honors the PYTHONPATH=. standing rule (R10).

ANTLR_JAR := grammar/antlr-4.13.2-complete.jar
PY := PYTHONPATH=src:. python

.PHONY: help install dev antlr-gen test smoke up down experiments figures tables paper clean

help:
	@echo "Targets:"
	@echo "  install      pip install -e . (runtime deps)"
	@echo "  dev          pip install -e '.[dev]' (adds pytest, hypothesis, matplotlib, linters)"
	@echo "  antlr-gen    regenerate the ANTLR JSON parser into src/nsdsl/dsl/generated (needs Java)"
	@echo "  test         run the full pytest suite"
	@echo "  smoke        import-check the package"
	@echo "  up / down    bring the Docker microservices testbed up / down"
	@echo "  experiments  run the experiment harness -> results/raw/*.csv"
	@echo "  figures      regenerate all paper figures from per_config_summary.csv"
	@echo "  tables       regenerate all paper tables from per_config_summary.csv"

install:
	pip install -e .

dev:
	pip install -e '.[dev]'

antlr-gen:
	rm -f src/nsdsl/dsl/generated/JSON*.py src/nsdsl/dsl/generated/JSON*.tokens \
		src/nsdsl/dsl/generated/JSON*.interp
	cd grammar && java -jar antlr-4.13.2-complete.jar -Dlanguage=Python3 -visitor -listener \
		-o ../src/nsdsl/dsl/generated JSON.g4

test:
	$(PY) -m pytest -q tests/

smoke:
	$(PY) -c "import nsdsl; from nsdsl.neutro import SVNN, svnnwaa, svnnwga, score; print('nsdsl OK', nsdsl.__version__)"

up:
	docker compose -f docker/docker-compose.yml up -d --build

down:
	docker compose -f docker/docker-compose.yml down -v

experiments:
	$(PY) experiments/run_all.py

figures:
	$(PY) experiments/make_figures.py

tables:
	$(PY) experiments/make_tables.py

paper:
	cd paper && latexmk -pdf manuscript.tex

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .hypothesis **/__pycache__
