# Airpine justfile - Common development commands

# List all available commands
default:
    @just --list

# Install dependencies with uv
install:
    uv pip install -e ".[dev]"

# Run unit tests
test:
    uv run pytest tests/ -v

# Run specific test file
test-file FILE:
    uv run pytest tests/{{FILE}} -v

# Lint with ruff
check:
    uv run ruff check airpine/ tests/
    uv run ruff format airpine/ tests/
    uv run mypy airpine/

# Auto-fix linting issues
fix:
    uv run ruff check --fix airpine/ tests/
    uv run ruff format airpine/ tests/

# Clean up generated files
clean:
    rm -rf .pytest_cache __pycache__ .mypy_cache .ruff_cache
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    rm -rf htmlcov .coverage

# Run the demo app
demo:
    uv run python examples/demo.py

# Run a Python REPL with airpine imported
repl:
    uv run python -i -c "from airpine import Alpine, RawJS; print('Alpine and RawJS imported')"

# Build the package
publish:
    uv build
    uv publish