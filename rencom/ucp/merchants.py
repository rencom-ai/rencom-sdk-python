"""UCP merchant discovery client.

Search and discover merchants on the Universal Commerce Protocol.
"""

from collections.abc import AsyncIterator
from typing import Any

from rencom._generated.models import MerchantDetails, MerchantSearchResponse, MerchantSearchResult
from rencom._http import HTTPClient


class MerchantClient:
    """Client for UCP merchant discovery.

    Search for merchants by capabilities, industry, region, and other
    filters. Merchants expose UCP capabilities like checkout, shopping
    cart, order management, etc.

    Example:
        >>> merchants = await client.ucp.merchants.search(
        ...     capabilities=["dev.ucp.shopping.checkout"],
        ...     industry="retail",
        ...     region="US"
        ... )
        >>> for merchant in merchants.merchants:
        ...     print(merchant.name, merchant.domain)
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the merchant client."""
        self._http = http_client

    async def search(
        self,
        *,
        capabilities: list[str] | None = None,
        industry: str | None = None,
        region: str | None = None,
        has_catalog: bool | None = None,
        limit: int = 20,
        offset: int = 0,
        session_id: str | None = None,
    ) -> MerchantSearchResponse:
        """Search for UCP merchants.

        Args:
            capabilities: Filter by UCP capabilities
                (e.g., ["dev.ucp.shopping.checkout"])
            industry: Filter by industry (e.g., "retail", "electronics")
            region: Filter by region code (e.g., "US", "EU")
            has_catalog: Filter for merchants with native catalog API
            limit: Number of results (1-100). Defaults to 20.
            offset: Pagination offset
            session_id: Session ID for analytics tracking

        Returns:
            MerchantSearchResponse with merchants and pagination

        Example:
            >>> # Find retail merchants with checkout capability
            >>> merchants = await client.ucp.merchants.search(
            ...     capabilities=["dev.ucp.shopping.checkout"],
            ...     industry="retail"
            ... )
            >>> for merchant in merchants.merchants:
            ...     print(merchant.name)
        """
        # Build query parameters
        params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }

        if capabilities:
            params["capabilities"] = capabilities
        if industry:
            params["industry"] = industry
        if region:
            params["region"] = region
        if has_catalog is not None:
            params["has_catalog"] = has_catalog
        if session_id:
            params["session_id"] = session_id

        # Make request
        response_data = await self._http.get("/ucp/v1/merchants", params=params)

        # Parse response
        return MerchantSearchResponse.model_validate(response_data)

    async def get(self, domain: str) -> MerchantDetails:
        """Get details for a specific merchant.

        Args:
            domain: Merchant domain (e.g., "example.com")

        Returns:
            MerchantDetails object with full details

        Raises:
            NotFoundError: If merchant not found

        Example:
            >>> merchant = await client.ucp.merchants.get("example.com")
            >>> print(merchant.name, merchant.capabilities)
        """
        response_data = await self._http.get(f"/ucp/v1/merchants/{domain}")
        return MerchantDetails.model_validate(response_data)

    async def search_iter(
        self,
        *,
        capabilities: list[str] | None = None,
        industry: str | None = None,
        region: str | None = None,
        has_catalog: bool | None = None,
        limit: int = 20,
        session_id: str | None = None,
    ) -> AsyncIterator[MerchantSearchResult]:
        """Auto-paginate through merchant search results.

        Yields merchants one at a time, automatically handling pagination.

        Args:
            Same as search(), except no offset parameter

        Yields:
            MerchantSearchResult objects one at a time

        Example:
            >>> async for merchant in client.ucp.merchants.search_iter(industry="retail"):
            ...     print(merchant.domain)
            ...     if enough_merchants:
            ...         break
        """
        offset = 0
        while True:
            # Fetch page
            page = await self.search(
                capabilities=capabilities,
                industry=industry,
                region=region,
                has_catalog=has_catalog,
                limit=limit,
                offset=offset,
                session_id=session_id,
            )

            # Yield merchants one at a time
            for merchant in page.merchants:
                yield merchant

            # Check if more results are available
            if not page.has_more:
                break

            # Move to next page
            offset += limit
