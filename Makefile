install:
	poetry install

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov

lint:
	poetry run flake8 page_loader
	poetry run flake8 tests

selfcheck:
	poetry check

check: selfcheck test lint

build: check
	poetry build

run:
	poetry run page_loader/scripts/main.py -o tmp $(ARGS)

.PHONY: install test lint selfcheck check build