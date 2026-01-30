# Rencom Python SDK

Official Python SDK for the [Rencom API](https://api.rencom.ai) - unified search for x402 resources and UCP merchants.

[![PyPI](https://img.shields.io/pypi/v/rencom.svg)](https://pypi.org/project/rencom/)
[![Python Versions](https://img.shields.io/pypi/pyversions/rencom.svg)](https://pypi.org/project/rencom/)
[![License](https://img.shields.io/github/license/rencom-ai/rencom-sdk-python.svg)](https://github.com/rencom-ai/rencom-sdk-python/blob/main/LICENSE)
[![Tests](https://github.com/rencom-ai/rencom-sdk-python/workflows/Tests/badge.svg)](https://github.com/rencom-ai/rencom-sdk-python/actions)

## Features

- 🔍 **x402 Resource Search** - Discover APIs that accept blockchain payments
- 🏪 **UCP Merchant Discovery** - Find merchants and products on the Universal Commerce Protocol
- 🔐 **Multiple Auth Methods** - API keys, JWT, x402 payments
- 📊 **Built-in Analytics** - Session tracking and click logging
- ⚡ **Async First** - Built on httpx with full async/await support
- 🛡️ **Type Safe** - Fully typed with Pydantic models
- 🔄 **Auto-pagination** - Iterate through large result sets effortlessly

## Installation

```bash
pip install rencom
```

### Optional Dependencies

```bash
# CLI tools
pip install rencom[cli]

# x402 payment support
pip install rencom[x402]

# Development dependencies
pip install rencom[dev]
```

## Quick Start

```python
import asyncio
from rencom import AsyncRencomClient

async def main():
    # Initialize client with API key
    async with AsyncRencomClient(api_key="rk_...") as client:
        # Search x402 resources
        results = await client.x402.search("trading api")
        for result in results.results:
            print(f"{result.resource}: {result.description}")

        # Search UCP merchants
        merchants = await client.ucp.merchants.search(industry="retail")
        for merchant in merchants.results:
            print(f"{merchant.name}: {merchant.domain}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

- [Full Documentation](https://rencom-sdk-python.readthedocs.io)
- [API Reference](https://rencom-sdk-python.readthedocs.io/reference/)
- [Examples](https://github.com/rencom-ai/rencom-sdk-python/tree/main/examples)
- [Changelog](https://github.com/rencom-ai/rencom-sdk-python/blob/main/CHANGELOG.md)

## Authentication

### API Key (Recommended)

```python
from rencom import AsyncRencomClient

client = AsyncRencomClient(api_key="rk_...")
```

### Environment Variable

```bash
export RENCOM_API_KEY="rk_..."
```

```python
client = AsyncRencomClient()  # Auto-loads from env
```

### JWT Token

```python
# After email verification
client = AsyncRencomClient(jwt_token="eyJ...")
```

## Usage Examples

See the [examples/](./examples) directory for full working examples.

## Development

### Setup

```bash
git clone https://github.com/rencom-ai/rencom-sdk-python.git
cd rencom-sdk-python

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Testing

```bash
# Run all tests
pytest

# Run only unit tests (fast)
pytest -m unit

# Run with coverage
pytest --cov=rencom --cov-report=html
```

### Code Generation

The SDK auto-generates code from the OpenAPI specification:

```bash
python scripts/generate.py
```

**Important:** Never edit files in `rencom/_generated/` manually - they will be overwritten.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](./LICENSE) for details.

## Support

- [Documentation](https://rencom-sdk-python.readthedocs.io)
- [Issue Tracker](https://github.com/rencom-ai/rencom-sdk-python/issues)
- [Discussions](https://github.com/rencom-ai/rencom-sdk-python/discussions)
