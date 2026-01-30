"""Main client classes for the Rencom SDK.

This module provides the high-level client interface that users interact with.
It delegates to namespace-specific clients (x402, ucp, auth) and manages
HTTP connections, authentication, and rate limiting.
"""

import os
from typing import Any

from rencom._http import HTTPClient
from rencom.auth import AuthClient
from rencom.ucp import UCPNamespace
from rencom.x402 import X402Client


class AsyncRencomClient:
    """Async client for the Rencom API.

    This is the main entry point for interacting with the Rencom API.
    It provides namespaced access to different API sections:
    - x402: Resource search with blockchain payments
    - ucp.merchants: Merchant discovery
    - ucp.products: Product search
    - ucp.analytics: Click tracking
    - auth: Authentication and account management

    Args:
        api_key: API key for authentication. If not provided, will attempt
            to load from RENCOM_API_KEY environment variable.
        jwt_token: JWT token for user-authenticated endpoints. Mutually
            exclusive with api_key.
        base_url: Base URL for the API. Defaults to https://api.rencom.ai
        timeout: Request timeout in seconds. Defaults to 30.0.
        max_retries: Maximum number of retry attempts for failed requests.
            Defaults to 3.
        auto_retry_rate_limits: Whether to automatically retry when rate
            limited. Defaults to False.

    Example:
        >>> async with AsyncRencomClient(api_key="rk_...") as client:
        ...     # Search x402 resources
        ...     results = await client.x402.search("weather api")
        ...     # Search UCP merchants
        ...     merchants = await client.ucp.merchants.search(industry="retail")
        ...     # Search UCP products
        ...     products = await client.ucp.products.search("laptop")

    Attributes:
        x402: X402Client for resource search
        ucp: UCPNamespace for merchant/product discovery and analytics
        auth: AuthClient for authentication and account management
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        jwt_token: str | None = None,
        base_url: str = "https://api.rencom.ai",
        timeout: float = 30.0,
        max_retries: int = 3,
        auto_retry_rate_limits: bool = False,
    ) -> None:
        """Initialize the async Rencom client."""
        # Get API key from environment if not provided
        if api_key is None and jwt_token is None:
            api_key = os.environ.get("RENCOM_API_KEY")

        if api_key is None and jwt_token is None:
            raise ValueError(
                "Either api_key or jwt_token must be provided, or RENCOM_API_KEY "
                "environment variable must be set"
            )

        # Create HTTP client
        self._http = HTTPClient(
            api_key=api_key,
            jwt_token=jwt_token,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            auto_retry_rate_limits=auto_retry_rate_limits,
        )

        # Initialize namespace clients
        self.x402 = X402Client(self._http)
        self.ucp = UCPNamespace(self._http)
        self.auth = AuthClient(self._http)

    async def __aenter__(self) -> "AsyncRencomClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._http.close()


class RencomClient:
    """Synchronous wrapper around AsyncRencomClient.

    This provides a synchronous interface by running async operations
    in an event loop. For better performance, prefer AsyncRencomClient
    when possible.

    Args:
        Same as AsyncRencomClient

    Example:
        >>> with RencomClient(api_key="rk_...") as client:
        ...     results = client.x402.search("weather api")
        ...     print(results.results[0].resource)
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        jwt_token: str | None = None,
        base_url: str = "https://api.rencom.ai",
        timeout: float = 30.0,
        max_retries: int = 3,
        auto_retry_rate_limits: bool = False,
    ) -> None:
        """Initialize the sync Rencom client."""
        import asyncio

        # Create async client
        self._async_client = AsyncRencomClient(
            api_key=api_key,
            jwt_token=jwt_token,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            auto_retry_rate_limits=auto_retry_rate_limits,
        )

        # Create and store event loop for sync operations
        try:
            self._loop = asyncio.get_event_loop()
            if self._loop.is_closed():
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

        # Wrap sub-clients with sync wrappers (pass the loop)
        from rencom.auth import SyncAuthClient
        from rencom.ucp import SyncUCPNamespace
        from rencom.x402 import SyncX402Client

        self.x402 = SyncX402Client(self._async_client.x402, self._loop)
        self.ucp = SyncUCPNamespace(self._async_client.ucp, self._loop)
        self.auth = SyncAuthClient(self._async_client.auth, self._loop)

    def __enter__(self) -> "RencomClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the client and release resources."""
        if hasattr(self, "_loop") and not self._loop.is_closed():
            self._loop.run_until_complete(self._async_client.close())
