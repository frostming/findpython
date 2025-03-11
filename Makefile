checkfiles = src/ tests/

help:
	@echo  "FindPython development makefile"
	@echo
	@echo  "Usage: make <target>"
	@echo  "Targets:"
	@echo  "    up      Updates dev/test dependencies"
	@echo  "    deps    Ensure dev/test dependencies are installed"
	@echo  "    check   Checks that build is sane"
	@echo  "    test    Runs all tests"
	@echo  "    style   Auto-formats the code"
	@echo  "    lint    Auto-formats the code and check type hints"

up:
	pdm update --verbose

deps:
ifeq ($(wildcard .venv),)
	pdm install --verbose
else
	pdm install
endif

_check:
	pdm run ruff format --check $(checkfiles)
	pdm run ruff check $(checkfiles)
	pdm run mypy $(checkfiles)
check: deps _build _check

_style:
	pdm run ruff format $(checkfiles)
	pdm run ruff check --fix $(checkfiles)
style: deps _style

_lint:
	pdm run ruff format $(checkfiles)
	pdm run ruff check --fix $(checkfiles)
	pdm run mypy $(checkfiles)
lint: deps _build _lint

_test:
	pdm run pytest -s tests
test: deps _test

_build:
	rm -fR dist/
	pdm build
build: deps _build

# Usage::
#   make venv version=3.12
venv:
	pdm venv create $(version)
	pdm run pip install --upgrade pip
