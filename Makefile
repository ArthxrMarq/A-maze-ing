PYTHON ?= python3
CONFIG ?= config.txt

.PHONY: install run debug clean lint build

install:
	$(PYTHON) -m pip install -r requirements-dev.txt
	$(PYTHON) -m pip install --no-build-isolation -e .

run:
	$(PYTHON) a_maze_ing.py "$(CONFIG)"

debug:
	$(PYTHON) -m pdb a_maze_ing.py "$(CONFIG)"

clean:
	find . -type d \( -name .git -o -name .venv -o -name venv \) -prune -o -type d \( -name __pycache__ -o -name .mypy_cache \) -exec rm -rf {} +

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

build:
	$(PYTHON) -m build --wheel --no-isolation --outdir .
