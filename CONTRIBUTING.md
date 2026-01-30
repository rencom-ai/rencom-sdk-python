# Contributing to Rencom Python SDK

Thank you for your interest in contributing! This guide will help you get started.

## Architecture

The SDK uses a **hybrid generated + hand-crafted architecture**:

- `rencom/_generated/` - Auto-generated from OpenAPI spec. **DO NOT EDIT MANUALLY.**
- `rencom/*.py` - Hand-crafted wrapper code. Edit freely.
- `tests/` - Test suite. Add tests for any new features.

### Why This Architecture?

The API is evolving rapidly. Auto-generating the low-level client ensures the SDK stays in sync with minimal maintenance, while hand-crafted wrappers provide a great developer experience.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git

### Setup Steps

```bash
# Clone the repository
git clone https://github.com/rencom-ai/rencom-sdk-python.git
cd rencom-sdk-python

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- **For new features**: Add code to `rencom/` (not `rencom/_generated/`)
- **For bug fixes**: Fix in the appropriate module
- **For API changes**: Run `python scripts/generate.py` to regenerate

### 3. Write Tests

Add tests to the appropriate file:

- `tests/unit/` - Fast tests with no external dependencies
- `tests/integration/` - Tests against live API (marked with `@pytest.mark.integration`)

```python
# tests/unit/test_x402.py
import pytest
from rencom import AsyncRencomClient

@pytest.mark.unit
async def test_x402_search_validates_params():
    client = AsyncRencomClient(api_key="test")
    with pytest.raises(ValueError):
        await client.x402.search(query="", limit=-1)
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run only unit tests (fast)
pytest -m unit

# Run with coverage
pytest --cov=rencom --cov-report=html

# Run specific test file
pytest tests/unit/test_x402.py
```

### 5. Lint and Format

```bash
# Auto-format code
ruff format .

# Lint code
ruff check .

# Type check
mypy rencom/
```

Pre-commit hooks will run these automatically on commit.

### 6. Commit

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
git commit -m "feat: add auto-pagination for x402 search"
git commit -m "fix: handle rate limit errors correctly"
git commit -m "docs: update authentication examples"
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### 7. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Regenerating Code from OpenAPI

If the API has changed and you need to regenerate the client:

```bash
python scripts/generate.py
```

This will:
1. Download the latest OpenAPI spec from the API
2. Generate code in `rencom/_generated/`
3. Report any breaking changes

**Note:** This is usually done automatically by CI when the API changes.

## Testing Guidelines

### Unit Tests (Preferred)

- Fast, no external dependencies
- Mock HTTP responses with `respx`
- Mark with `@pytest.mark.unit`

```python
import respx
from httpx import Response

@pytest.mark.unit
@respx.mock
async def test_x402_search():
    respx.get("https://api.rencom.ai/x402/v1/search").mock(
        return_value=Response(200, json={"results": []})
    )
    client = AsyncRencomClient(api_key="test")
    results = await client.x402.search("test")
    assert results.results == []
```

### Integration Tests

- Test against live API (or staging)
- Mark with `@pytest.mark.integration`
- Require valid API key in environment

```python
import os
import pytest

@pytest.mark.integration
async def test_x402_search_live():
    api_key = os.getenv("RENCOM_API_KEY")
    if not api_key:
        pytest.skip("RENCOM_API_KEY not set")

    client = AsyncRencomClient(api_key=api_key)
    results = await client.x402.search("weather")
    assert len(results.results) > 0
```

### Recording HTTP Interactions (VCR)

Use VCR.py to record real API responses for testing:

```python
import vcr

@vcr.use_cassette('tests/fixtures/vcr_cassettes/x402_search.yaml')
async def test_x402_search_recorded():
    # First run: records real API response
    # Subsequent runs: replays from cassette
    client = AsyncRencomClient(api_key="test")
    results = await client.x402.search("weather")
    assert len(results.results) > 0
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
async def search(
    self,
    query: str,
    *,
    sort_by: str = "recommended",
    limit: int = 3,
) -> SearchResponse:
    """Search x402 resources with semantic ranking.

    Args:
        query: Search query (e.g., "trading api", "weather data").
        sort_by: Sort order. One of: recommended, price_low, price_high,
            newest, most_popular, most_used. Defaults to recommended.
        limit: Number of results (1-5). Defaults to 3.

    Returns:
        SearchResponse with results, pagination info, and rate limits.

    Raises:
        RateLimitError: When rate limit is exceeded.
        ValidationError: When parameters are invalid.

    Example:
        >>> results = await client.x402.search("weather api")
        >>> print(results.results[0].resource)
        https://api.weather.com/v1/forecast
    """
```

### Examples

Add runnable examples to `examples/`:

```python
# examples/x402_search.py
"""Basic x402 search example."""
import asyncio
from rencom import AsyncRencomClient

async def main():
    client = AsyncRencomClient(api_key="rk_test_...")
    results = await client.x402.search("weather api")
    for result in results.results:
        print(f"{result.resource}: {result.description}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Common Tasks

### Adding a New Feature

1. Check if it needs to be in generated code (API change) or wrapper code (SDK improvement)
2. Write tests first (TDD approach)
3. Implement the feature
4. Update docstrings
5. Add example to `examples/`

### Fixing a Bug

1. Write a failing test that reproduces the bug
2. Fix the bug
3. Verify the test passes
4. Add regression test if needed

### Updating Dependencies

```bash
# Update a specific dependency
pip install --upgrade httpx

# Update all dependencies
pip install --upgrade -e ".[dev]"

# Update lockfile
pip freeze > requirements.txt
```

## Release Process

Releases are automated via GitHub Actions when a tag is pushed:

```bash
# Update version in pyproject.toml
# Update CHANGELOG.md

git add pyproject.toml CHANGELOG.md
git commit -m "chore: release v0.2.0"
git tag v0.2.0
git push origin main --tags
```

## Getting Help

- 💬 [GitHub Discussions](https://github.com/rencom-ai/rencom-sdk-python/discussions) - Ask questions
- 🐛 [Issue Tracker](https://github.com/rencom-ai/rencom-sdk-python/issues) - Report bugs
- 📖 [Documentation](https://rencom-sdk-python.readthedocs.io) - Read the docs

## Code of Conduct

Be respectful, inclusive, and considerate. We're all here to build great software together.
