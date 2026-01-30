"""UCP analytics client for tracking search behavior."""

from rencom._http import HTTPClient


class AnalyticsClient:
    """Client for UCP analytics tracking.

    Track user interactions with search results, including clicks
    on products and merchants. This helps improve search ranking
    and provides usage insights.

    Example:
        >>> # After user clicks a product
        >>> await client.ucp.analytics.log_click(
        ...     search_log_id=results.search_log_id,
        ...     clicked_product_id=results.products[0].id,
        ...     clicked_position=0
        ... )
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the analytics client."""
        self._http = http_client

    async def log_click(
        self,
        search_log_id: int,
        *,
        clicked_product_id: int | None = None,
        clicked_merchant_id: int | None = None,
        clicked_position: int | None = None,
    ) -> None:
        """Log a click event on a search result.

        Tracks when users click on products or merchants from search
        results. This data improves search ranking and provides analytics.

        Args:
            search_log_id: Search log ID from the search response (required)
            clicked_product_id: Product ID that was clicked
            clicked_merchant_id: Merchant ID that was clicked
            clicked_position: Position of the clicked result (0-indexed)

        Example:
            >>> # After product search
            >>> results = await client.ucp.products.search("laptop")
            >>>
            >>> # User clicks first result
            >>> await client.ucp.analytics.log_click(
            ...     search_log_id=results.search_log_id,
            ...     clicked_product_id=results.products[0].id,
            ...     clicked_position=0
            ... )
            >>>
            >>> # After merchant search
            >>> merchants = await client.ucp.merchants.search(industry="retail")
            >>>
            >>> # User clicks second merchant
            >>> await client.ucp.analytics.log_click(
            ...     search_log_id=merchants.search_log_id,
            ...     clicked_merchant_id=merchants.merchants[1].id,
            ...     clicked_position=1
            ... )
        """
        # Build query parameters
        params = {"search_log_id": search_log_id}

        if clicked_product_id is not None:
            params["clicked_product_id"] = clicked_product_id
        if clicked_merchant_id is not None:
            params["clicked_merchant_id"] = clicked_merchant_id
        if clicked_position is not None:
            params["clicked_position"] = clicked_position

        # Make request (no response body expected)
        await self._http.post("/ucp/v1/analytics/click", json=params)
