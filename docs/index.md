# Rencom Python SDK

Official Python SDK for the [Rencom API](https://api.rencom.ai) - unified search for x402 resources and UCP merchants.

## Features

- **x402 Resource Search** - Discover APIs that accept blockchain payments
- **UCP Merchant Discovery** - Find merchants on the Universal Commerce Protocol
- **UCP Product Search** - Search products across merchant catalogs
- **Multiple Auth Methods** - API keys, JWT tokens, x402 payments
- **Built-in Analytics** - Session tracking and click logging
- **Async First** - Built on httpx with full async/await support
- **Type Safe** - Fully typed with Pydantic models
- **Auto-pagination** - Iterate through large result sets effortlessly

## Installation

```bash
pip install rencom
```

## Quick Example

```python
import asyncio
from rencom import AsyncRencomClient

async def main():
    async with AsyncRencomClient(api_key="rk_...") as client:
        # Search x402 resources
        results = await client.x402.search("weather api")
        for result in results.results:
            print(f"{result.resource}: {result.description}")

        # Search UCP merchants
        merchants = await client.ucp.merchants.search(industry="retail")
        for merchant in merchants.results:
            print(f"{merchant.name}: {merchant.domain}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

- [Installation Guide](getting-started/installation.md)
- [Quick Start Tutorial](getting-started/quickstart.md)
- [Authentication Methods](getting-started/authentication.md)
- [API Reference](reference/client.md)
- [Examples](examples/x402.md)

## Support

- [GitHub Issues](https://github.com/rencom-ai/rencom-sdk-python/issues)
- [Discussions](https://github.com/rencom-ai/rencom-sdk-python/discussions)
- [API Documentation](https://api.rencom.ai/docs)
