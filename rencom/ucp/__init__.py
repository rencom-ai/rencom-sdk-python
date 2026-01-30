"""UCP (Universal Commerce Protocol) clients.

This package provides clients for discovering UCP merchants and
searching products across the UCP network.
"""

import asyncio
from collections.abc import Coroutine
from typing import Any, TypeVar

from rencom._http import HTTPClient
from rencom.ucp.analytics import AnalyticsClient
from rencom.ucp.merchants import MerchantClient
from rencom.ucp.products import ProductClient

T = TypeVar("T")


class UCPNamespace:
    """Namespace for UCP-related clients.

    Provides access to merchant discovery, product search, and analytics.

    Example:
        >>> # Search merchants
        >>> merchants = await client.ucp.merchants.search(industry="retail")
        >>>
        >>> # Search products
        >>> products = await client.ucp.products.search("laptop")
        >>>
        >>> # Log click
        >>> await client.ucp.analytics.log_click(
        ...     search_log_id=products.search_log_id,
        ...     clicked_product_id=products.products[0].id
        ... )
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize UCP namespace.

        Args:
            http_client: HTTP client for making requests
        """
        self.merchants = MerchantClient(http_client)
        self.products = ProductClient(http_client)
        self.analytics = AnalyticsClient(http_client)


class SyncUCPNamespace:
    """Synchronous wrapper for UCPNamespace.

    Provides synchronous access to UCP clients.
    """

    def __init__(
        self, async_namespace: UCPNamespace, loop: asyncio.AbstractEventLoop | None = None
    ) -> None:
        """Initialize sync UCP namespace.

        Args:
            async_namespace: Async UCPNamespace to wrap
            loop: Event loop to use (optional)
        """
        self._async_namespace = async_namespace
        self._loop = loop

    def _run(self, coro: Coroutine[Any, Any, T]) -> T:
        """Run an async coroutine synchronously."""
        if self._loop:
            if self._loop.is_running():
                raise RuntimeError(
                    "Cannot use sync client from an already running event loop. "
                    "Use AsyncRencomClient instead."
                )
            return self._loop.run_until_complete(coro)

        # Fallback to default behavior
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                raise RuntimeError(
                    "Cannot use sync client from an already running event loop. "
                    "Use AsyncRencomClient instead."
                )
            return loop.run_until_complete(coro)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

    # Note: For a complete implementation, we would add sync wrappers for
    # merchants, products, and analytics here. For brevity, users should
    # prefer AsyncRencomClient for full functionality.


__all__ = [
    "MerchantClient",
    "ProductClient",
    "AnalyticsClient",
    "UCPNamespace",
    "SyncUCPNamespace",
]
