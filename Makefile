.PHONY: lint test build clean all format deps-testing

deps-testing:
	@echo "Installing package with testing dependencies..."
	pip install -e ".[testing]"

all: format lint test build

format:
	@echo "Running ruff formatter..."
	ruff format src/ tests/

lint:
	@echo "Running ruff linter and formatter..."
	ruff check src/ tests/
	ruff format --check src/ tests/

test:
	@echo "Running tests..."
	pytest

test-capture:
	@echo "Running tests with output capture..."
	pytest --capture-output

build: clean
	@echo "Building package..."
	python -m build

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info/ 