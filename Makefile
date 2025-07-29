# ========================
# Development Tools (uv)
# ========================

.PHONY: help
help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

sync:  ## Sync dependencies from pyproject.toml
	uv sync

install-dist:  ## Install latest build wheel (dist/*.whl)
	 uv tool install $$(ls -t dist/*.whl | head -n 1)

reinstall-dist:  ## Reinstall latest built wheel via uv tool
	@uv tool uninstall hexlet-code || true
	@uv tool install $(ls -t dist/*.whl | head -n 1)

build:  ## Build the project (wheel)
	uv build

run:  ## Run the app with arguments: ARGS="url -o tmp"
	uv run python3 page_loader/scripts/main.py $(ARGS)

# ========================
# Linting & Formatting
# ========================

lint:  ## Run all linters (ruff + djlint)
	uv run ruff check page_loader

lint-fix:  ## Auto-fix linting issues using ruff
	@uv run ruff check --fix page_loader

format:  ## Format code with Ruff
	uv run ruff format page_loader

# ========================
# Testing & Coverage
# ========================

test:  ## Run tests
	uv run pytest -v $(NAME)

test-cov:  ## Run tests with coverage
	uv run pytest --cov

test-coverage:  ## Full coverage report for `page_loader`
	uv run pytest --cov=page_loader --cov-report xml

check:  ## Run lint + test
	$(MAKE) lint
	$(MAKE) test

.PHONY: sync install-dist selfcheck build run lint format test test-cov test-coverage check
