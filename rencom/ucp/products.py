"""UCP product search client.

Search products across UCP merchant catalogs.
"""

from collections.abc import AsyncIterator
from typing import Literal

from rencom._generated.models import ProductSearchResponse, ProductSearchResult
from rencom._http import HTTPClient

Condition = Literal["new", "used", "refurbished"]


class ProductClient:
    """Client for UCP product search.

    Search products across merchant catalogs on the UCP network.
    Supports filtering by price, category, brand, condition, and
    specific merchants.

    Example:
        >>> products = await client.ucp.products.search(
        ...     "laptop",
        ...     price_max=150000,  # $1500 in cents
        ...     category="electronics"
        ... )
        >>> for product in products.products:
        ...     print(product.name, product.price_cents / 100)
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the product client."""
        self._http = http_client

    async def search(
        self,
        query: str,
        *,
        price_min: int | None = None,
        price_max: int | None = None,
        category: str | None = None,
        categories: list[str] | None = None,
        brand: str | None = None,
        condition: Condition | None = None,
        merchant_domains: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
        session_id: str | None = None,
    ) -> ProductSearchResponse:
        """Search for products across UCP merchants.

        Args:
            query: Search query (e.g., "laptop", "running shoes")
            price_min: Minimum price in cents (e.g., 5000 = $50.00)
            price_max: Maximum price in cents
            category: Single category filter
            categories: Multiple category filter
            brand: Brand filter
            condition: Product condition ("new", "used", "refurbished")
            merchant_domains: Limit search to specific merchants
            limit: Number of results (1-100). Defaults to 20.
            offset: Pagination offset
            session_id: Session ID for analytics tracking

        Returns:
            ProductSearchResponse with products and pagination

        Example:
            >>> # Search for laptops under $1500
            >>> products = await client.ucp.products.search(
            ...     "laptop",
            ...     price_max=150000,
            ...     category="electronics",
            ...     condition="new"
            ... )
            >>> for product in products.products:
            ...     print(product.name, f"${product.price_cents / 100:.2f}")
            >>>
            >>> # Search specific merchants
            >>> products = await client.ucp.products.search(
            ...     "shoes",
            ...     merchant_domains=["nike.com", "adidas.com"]
            ... )
        """
        # Build query parameters
        params = {
            "q": query,
            "limit": limit,
            "offset": offset,
        }

        if price_min is not None:
            params["price_min"] = price_min
        if price_max is not None:
            params["price_max"] = price_max
        if category:
            params["category"] = category
        if categories:
            params["categories"] = categories
        if brand:
            params["brand"] = brand
        if condition:
            params["condition"] = condition
        if merchant_domains:
            params["merchant_domains"] = merchant_domains
        if session_id:
            params["session_id"] = session_id

        # Make request
        response_data = await self._http.get("/ucp/v1/products/search", params=params)

        # Parse response
        return ProductSearchResponse.model_validate(response_data)

    async def search_iter(
        self,
        query: str,
        *,
        price_min: int | None = None,
        price_max: int | None = None,
        category: str | None = None,
        categories: list[str] | None = None,
        brand: str | None = None,
        condition: Condition | None = None,
        merchant_domains: list[str] | None = None,
        limit: int = 20,
        session_id: str | None = None,
    ) -> AsyncIterator[ProductSearchResult]:
        """Auto-paginate through product search results.

        Yields products one at a time, automatically handling pagination.

        Args:
            Same as search(), except no offset parameter

        Yields:
            ProductSearchResult objects one at a time

        Example:
            >>> async for product in client.ucp.products.search_iter("laptop"):
            ...     print(product.name, product.price_cents)
            ...     if product.price_cents > 200000:  # Over $2000
            ...         break
        """
        offset = 0
        while True:
            # Fetch page
            page = await self.search(
                query,
                price_min=price_min,
                price_max=price_max,
                category=category,
                categories=categories,
                brand=brand,
                condition=condition,
                merchant_domains=merchant_domains,
                limit=limit,
                offset=offset,
                session_id=session_id,
            )

            # Yield products one at a time
            for product in page.products:
                yield product

            # Check if more results are available
            if not page.has_more:
                break

            # Move to next page
            offset += limit
