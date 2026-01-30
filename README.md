# Rencom Python SDK

Official Python SDK for the Rencom API.

[![PyPI](https://img.shields.io/pypi/v/rencom.svg)](https://pypi.org/project/rencom/)
[![Python Versions](https://img.shields.io/pypi/pyversions/rencom.svg)](https://pypi.org/project/rencom/)
[![License](https://img.shields.io/github/license/rencom-ai/rencom-sdk-python.svg)](https://github.com/rencom-ai/rencom-sdk-python/blob/main/LICENSE)

## Installation

```bash
pip install rencom
```

For x402 payment support:

```bash
pip install rencom[x402]
```

## Quick Start

```python
import asyncio
from rencom import AsyncRencomClient

async def main():
    async with AsyncRencomClient(api_key="rn_...") as client:
        # Search x402 resources
        results = await client.x402.search("trading api")
        for result in results.results:
            print(f"{result.resource}: {result.description}")

        # Search UCP merchants
        merchants = await client.ucp.merchants.search(industry="retail")
        for merchant in merchants.merchants:
            print(f"{merchant.name}: {merchant.domain}")

asyncio.run(main())
```

## Authentication

### Getting an API Key

1. Visit https://api.rencom.ai/login
2. Sign in with your email, Github or Google
3. Generate an API key from your dashboard

### Using Your API Key

The SDK supports multiple authentication methods:

**API Key** (recommended):
```python
client = AsyncRencomClient(api_key="rn_...")
```

**Environment Variable**:
```bash
export RENCOM_API_KEY="rn_..."
```
```python
client = AsyncRencomClient()  # Auto-loads from environment
```

**JWT Token**:
```python
client = AsyncRencomClient(jwt_token="eyJ...")
```

## Features

- x402 resource search - discover APIs that accept blockchain payments
- UCP merchant discovery - find merchants and products on the Universal Commerce Protocol
- Fully typed with Pydantic models
- Built-in pagination support
- Async/await support via httpx
- Session tracking and analytics

## Documentation

Full documentation coming soon.

See the [examples/](./examples) directory for more usage examples.

## Development

```bash
git clone https://github.com/rencom-ai/rencom-sdk-python.git
cd rencom-sdk-python
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

The SDK auto-generates models from the OpenAPI specification:
```bash
python scripts/generate.py
```

Note: Files in `rencom/_generated/` are auto-generated and should not be edited manually.

## License

MIT License - see [LICENSE](./LICENSE) for details.
