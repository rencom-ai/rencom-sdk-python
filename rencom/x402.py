"""x402 resource search client.

This module provides the high-level interface for searching x402 resources
(APIs that accept blockchain payments).
"""

import asyncio
from collections.abc import AsyncIterator, Coroutine, Iterator
from typing import Any, TypeVar

from rencom._generated.models import ResourceSearchResult, SearchResponse
from rencom._http import HTTPClient

T = TypeVar("T")


class X402Client:
    """Client for x402 resource search.

    Provides methods for searching APIs that accept x402 blockchain payments.
    Results are ranked using a combination of text relevance, semantic
    similarity, usage patterns, and quality metrics.

    Example:
        >>> results = await client.x402.search(
        ...     "weather api",
        ...     sort_by="recommended",
        ...     limit=5
        ... )
        >>> for result in results.results:
        ...     print(result.resource, result.description)
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the x402 client.

        Args:
            http_client: HTTP client for making requests
        """
        self._http = http_client

    async def search(
        self,
        query: str,
        *,
        sort_by: str = "recommended",
        limit: int = 3,
        offset: int = 0,
    ) -> SearchResponse:
        """Search x402 resources with semantic ranking.

        Searches across APIs that accept blockchain payments via x402 protocol.
        Results are ranked using multiple signals including text relevance,
        semantic embeddings, usage patterns, and quality scores.

        Args:
            query: Search query (e.g., "trading api", "weather data").
                Natural language queries work well due to semantic search.
            sort_by: Sort order. Options:
                - "recommended": Weighted combination of all ranking signals (default)
                - "price_low": Cheapest resources first
                - "price_high": Most expensive first
                - "newest": Most recently discovered
                - "most_popular": Highest popularity score
                - "most_used": Most total API calls
            limit: Number of results to return (1-5). Defaults to 3.
            offset: Pagination offset for fetching more results. Defaults to 0.

        Returns:
            SearchResponse containing:
                - results: List of SearchResult objects
                - has_more: Whether more results are available
                - query: The search query used
                - sort_by: The sort method used
                - rate limits: Current rate limit status

        Raises:
            ValidationError: If query is empty or limit is out of range
            RateLimitError: If rate limit is exceeded
            AuthenticationError: If API key is invalid

        Example:
            >>> # Basic search
            >>> results = await client.x402.search("weather api")
            >>> print(f"Found {len(results.results)} resources")
            >>>
            >>> # With custom sorting and pagination
            >>> results = await client.x402.search(
            ...     "trading data",
            ...     sort_by="price_low",
            ...     limit=5,
            ...     offset=10
            ... )
        """
        # Build query parameters
        params = {
            "q": query,
            "sort_by": sort_by,
            "limit": limit,
            "offset": offset,
        }

        # Make request
        response_data = await self._http.get("/x402/v1/search", params=params)

        # Parse response into SearchResponse model
        return SearchResponse.model_validate(response_data)

    async def search_iter(
        self,
        query: str,
        *,
        sort_by: str = "recommended",
        limit: int = 5,
    ) -> AsyncIterator[ResourceSearchResult]:
        """Auto-paginate through all search results.

        Automatically handles pagination, yielding results one at a time
        until all matching resources have been returned.

        Args:
            query: Search query
            sort_by: Sort order
            limit: Page size (results per request)

        Yields:
            SearchResult objects one at a time

        Example:
            >>> async for result in client.x402.search_iter("weather"):
            ...     print(result.resource)
            ...     if some_condition:
            ...         break  # Stop early if needed
        """
        offset = 0
        while True:
            # Fetch page
            page = await self.search(query, sort_by=sort_by, limit=limit, offset=offset)

            # Yield results one at a time
            for result in page.results:
                yield result

            # Check if more results are available
            if not page.has_more:
                break

            # Move to next page
            offset += limit

    async def paid_search(
        self,
        query: str,
        *,
        sort_by: str = "recommended",
        limit: int = 3,
        offset: int = 0,
    ) -> SearchResponse:
        """Search using x402 payment protocol instead of API key.

        Similar to search() but pays per call using blockchain payments
        via the x402 protocol. Requires x402[evm] optional dependency.

        This endpoint is discoverable in the x402 Bazaar marketplace.

        Args:
            Same as search()

        Returns:
            Same as search()

        Raises:
            ImportError: If x402[evm] is not installed
            Same exceptions as search()

        Example:
            >>> # Requires x402 setup
            >>> results = await client.x402.paid_search("api")

        Note:
            This requires additional configuration. See docs for details.
        """
        # Check x402 dependency
        try:
            import x402  # type: ignore[import-not-found]  # noqa: F401
        except ImportError as e:
            raise ImportError(
                "x402[evm] is required for paid search. Install with: pip install rencom[x402]"
            ) from e

        # Build query parameters
        params = {
            "q": query,
            "sort_by": sort_by,
            "limit": limit,
            "offset": offset,
        }

        # Make request to paid endpoint
        response_data = await self._http.get("/x402/v1/paid/search", params=params)

        # Parse response
        return SearchResponse.model_validate(response_data)


class SyncX402Client:
    """Synchronous wrapper for X402Client.

    Provides a synchronous interface by wrapping async operations.

    Example:
        >>> client = RencomClient(api_key="rk_...")
        >>> results = client.x402.search("weather api")
        >>> for result in results.results:
        ...     print(result.resource)
    """

    def __init__(
        self, async_client: X402Client, loop: asyncio.AbstractEventLoop | None = None
    ) -> None:
        """Initialize sync wrapper.

        Args:
            async_client: Async X402Client to wrap
            loop: Event loop to use (optional)
        """
        self._async_client = async_client
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

    def search(
        self,
        query: str,
        *,
        sort_by: str = "recommended",
        limit: int = 3,
        offset: int = 0,
    ) -> SearchResponse:
        """Synchronous version of search()."""
        return self._run(
            self._async_client.search(query, sort_by=sort_by, limit=limit, offset=offset)
        )

    def search_iter(
        self,
        query: str,
        *,
        sort_by: str = "recommended",
        limit: int = 5,
    ) -> Iterator[ResourceSearchResult]:
        """Synchronous version of search_iter()."""
        # Note: This is not a true sync iterator - it fetches all results first
        all_results: list[ResourceSearchResult] = []
        async_iter = self._async_client.search_iter(query, sort_by=sort_by, limit=limit)

        async def collect() -> None:
            async for result in async_iter:
                all_results.append(result)

        self._run(collect())
        return iter(all_results)

    def paid_search(
        self,
        query: str,
        *,
        sort_by: str = "recommended",
        limit: int = 3,
        offset: int = 0,
    ) -> SearchResponse:
        """Synchronous version of paid_search()."""
        return self._run(
            self._async_client.paid_search(query, sort_by=sort_by, limit=limit, offset=offset)
        )
