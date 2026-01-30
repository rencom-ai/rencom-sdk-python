"""Rencom Python SDK.

Official Python SDK for the Rencom API - unified search for x402 resources
and UCP merchants.

Example:
    >>> import asyncio
    >>> from rencom import AsyncRencomClient
    >>>
    >>> async def main():
    ...     async with AsyncRencomClient(api_key="rk_...") as client:
    ...         results = await client.x402.search("weather api")
    ...         print(results.results[0].resource)
    >>>
    >>> asyncio.run(main())
"""

from rencom.client import AsyncRencomClient, RencomClient
from rencom.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    RencomError,
    ValidationError,
)

# TODO: Import models from _generated after code generation
# from rencom._generated.models import SearchResponse, SearchResult, Merchant, Product

__version__ = "0.1.0"
__api_version__ = "2.0.0"  # Updated from API's OpenAPI spec

__all__ = [
    # Version info
    "__version__",
    "__api_version__",
    # Clients
    "AsyncRencomClient",
    "RencomClient",
    # Exceptions
    "RencomError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "NotFoundError",
    # TODO: Export models after generation
]
