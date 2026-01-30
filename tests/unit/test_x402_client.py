"""Unit tests for the X402Client."""

import pytest
import respx
from httpx import Response

from rencom import AsyncRencomClient
from rencom._http import HTTPClient
from rencom.x402 import X402Client


@pytest.mark.unit
@pytest.mark.asyncio
class TestX402Client:
    """Test suite for X402Client."""

    @respx.mock
    async def test_search_basic(self, sample_search_response):
        """Test basic search functionality."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        x402_client = X402Client(http_client)

        respx.get("https://api.test.com/x402/v1/search").mock(
            return_value=Response(200, json=sample_search_response)
        )

        result = await x402_client.search("trading api")

        assert len(result.results) == 1
        assert result.results[0].resource == "https://api.example.com/v1/trading"
        assert result.query == "trading api"
        assert result.has_more is False
        await http_client.close()

    @respx.mock
    async def test_search_with_parameters(self, sample_search_response):
        """Test search with custom parameters."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        x402_client = X402Client(http_client)

        route = respx.get("https://api.test.com/x402/v1/search").mock(
            return_value=Response(200, json=sample_search_response)
        )

        await x402_client.search("trading api", sort_by="price_low", limit=5, offset=10)

        # Verify parameters were sent correctly
        request = route.calls.last.request
        assert "q=trading+api" in str(request.url)
        assert "sort_by=price_low" in str(request.url)
        assert "limit=5" in str(request.url)
        assert "offset=10" in str(request.url)
        await http_client.close()

    @respx.mock
    async def test_search_iter(self):
        """Test auto-pagination with search_iter."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        x402_client = X402Client(http_client)

        # Mock multiple pages
        page1 = {
            "results": [
                {
                    "id": 1,
                    "resource": "https://api1.example.com",
                    "description": "API 1",
                    "max_amount_required": 1000,
                    "network": "base",
                    "final_score": 0.9,
                }
            ],
            "has_more": True,
            "limit": 1,
            "offset": 0,
            "query": "api",
            "sort_by": "recommended",
        }

        page2 = {
            "results": [
                {
                    "id": 2,
                    "resource": "https://api2.example.com",
                    "description": "API 2",
                    "max_amount_required": 2000,
                    "network": "base",
                    "final_score": 0.8,
                }
            ],
            "has_more": False,
            "limit": 1,
            "offset": 1,
            "query": "api",
            "sort_by": "recommended",
        }

        route = respx.get("https://api.test.com/x402/v1/search")
        route.side_effect = [
            Response(200, json=page1),
            Response(200, json=page2),
        ]

        # Collect all results
        results = []
        async for result in x402_client.search_iter("api", limit=1):
            results.append(result)

        assert len(results) == 2
        assert results[0].id == 1
        assert results[1].id == 2
        assert route.call_count == 2
        await http_client.close()

    @respx.mock
    async def test_search_iter_early_break(self):
        """Test early break in search_iter."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        x402_client = X402Client(http_client)

        page1 = {
            "results": [
                {
                    "id": 1,
                    "resource": "https://api1.example.com",
                    "description": "API 1",
                    "max_amount_required": 1000,
                    "network": "base",
                    "final_score": 0.9,
                },
                {
                    "id": 2,
                    "resource": "https://api2.example.com",
                    "description": "API 2",
                    "max_amount_required": 2000,
                    "network": "base",
                    "final_score": 0.8,
                },
            ],
            "has_more": True,
            "limit": 2,
            "offset": 0,
            "query": "api",
            "sort_by": "recommended",
        }

        route = respx.get("https://api.test.com/x402/v1/search")
        route.mock(return_value=Response(200, json=page1))

        # Break after first result
        results = []
        async for result in x402_client.search_iter("api"):
            results.append(result)
            break

        assert len(results) == 1
        assert results[0].id == 1
        # Should only make one request
        assert route.call_count == 1
        await http_client.close()

    @respx.mock
    async def test_paid_search_without_x402(self):
        """Test paid_search raises ImportError without x402 package."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        x402_client = X402Client(http_client)

        with pytest.raises(ImportError) as exc_info:
            await x402_client.paid_search("api")

        assert "x402[evm]" in str(exc_info.value)
        await http_client.close()

    @respx.mock
    async def test_search_via_client(self, sample_search_response):
        """Test search through AsyncRencomClient."""
        respx.get("https://api.test.com/x402/v1/search").mock(
            return_value=Response(200, json=sample_search_response)
        )

        async with AsyncRencomClient(api_key="test_key", base_url="https://api.test.com") as client:
            result = await client.x402.search("trading api")

        assert len(result.results) == 1
        assert result.results[0].resource == "https://api.example.com/v1/trading"

    @respx.mock
    async def test_search_empty_results(self):
        """Test search with no results."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        x402_client = X402Client(http_client)

        empty_response = {
            "results": [],
            "has_more": False,
            "limit": 3,
            "offset": 0,
            "query": "nonexistent",
            "sort_by": "recommended",
        }

        respx.get("https://api.test.com/x402/v1/search").mock(
            return_value=Response(200, json=empty_response)
        )

        result = await x402_client.search("nonexistent")

        assert len(result.results) == 0
        assert result.has_more is False
        await http_client.close()

    @respx.mock
    async def test_search_pagination(self):
        """Test manual pagination with offset."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        x402_client = X402Client(http_client)

        page1 = {
            "results": [
                {
                    "id": 1,
                    "resource": "https://api1.example.com",
                    "description": "API 1",
                    "max_amount_required": 1000,
                    "network": "base",
                    "final_score": 0.9,
                }
            ],
            "has_more": True,
            "limit": 1,
            "offset": 0,
            "query": "api",
            "sort_by": "recommended",
        }

        page2 = {
            "results": [
                {
                    "id": 2,
                    "resource": "https://api2.example.com",
                    "description": "API 2",
                    "max_amount_required": 2000,
                    "network": "base",
                    "final_score": 0.8,
                }
            ],
            "has_more": False,
            "limit": 1,
            "offset": 1,
            "query": "api",
            "sort_by": "recommended",
        }

        route = respx.get("https://api.test.com/x402/v1/search")
        route.side_effect = [
            Response(200, json=page1),
            Response(200, json=page2),
        ]

        # Fetch first page
        result1 = await x402_client.search("api", limit=1, offset=0)
        assert len(result1.results) == 1
        assert result1.has_more is True

        # Fetch second page
        result2 = await x402_client.search("api", limit=1, offset=1)
        assert len(result2.results) == 1
        assert result2.has_more is False

        await http_client.close()
