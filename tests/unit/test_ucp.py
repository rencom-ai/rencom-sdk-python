"""Unit tests for UCP clients."""

import pytest
import respx
from httpx import Response

from rencom import AsyncRencomClient
from rencom._http import HTTPClient
from rencom.ucp import UCPNamespace
from rencom.ucp.analytics import AnalyticsClient
from rencom.ucp.merchants import MerchantClient
from rencom.ucp.products import ProductClient


@pytest.mark.unit
@pytest.mark.asyncio
class TestMerchantClient:
    """Test suite for MerchantClient."""

    @respx.mock
    async def test_search_basic(self):
        """Test basic merchant search."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        merchant_client = MerchantClient(http_client)

        response_data = {
            "merchants": [
                {
                    "id": 1,
                    "domain": "shop.example.com",
                    "name": "Example Shop",
                    "industry": "retail",
                    "region": "US",
                    "capabilities": ["dev.ucp.shopping.checkout"],
                    "has_native_catalog": True,
                    "endpoints": {
                        "rest": "https://shop.example.com/ucp/v1",
                        "mcp": None,
                        "a2a": None,
                    },
                    "ucp_profile_url": "https://shop.example.com/.well-known/ucp",
                }
            ],
            "total": 1,
            "has_more": False,
            "limit": 20,
            "offset": 0,
            "session_id": "sess_123",
            "search_log_id": 456,
        }

        respx.get("https://api.test.com/ucp/v1/merchants").mock(
            return_value=Response(200, json=response_data)
        )

        result = await merchant_client.search(industry="retail")

        assert len(result.merchants) == 1
        assert result.merchants[0].domain == "shop.example.com"
        assert result.merchants[0].name == "Example Shop"
        assert result.has_more is False
        await http_client.close()

    @respx.mock
    async def test_search_with_filters(self):
        """Test merchant search with multiple filters."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        merchant_client = MerchantClient(http_client)

        response_data = {
            "merchants": [],
            "total": 0,
            "has_more": False,
            "limit": 10,
            "offset": 0,
            "session_id": "sess_123",
            "search_log_id": 456,
        }

        route = respx.get("https://api.test.com/ucp/v1/merchants").mock(
            return_value=Response(200, json=response_data)
        )

        await merchant_client.search(
            capabilities=["dev.ucp.shopping.checkout"],
            industry="retail",
            region="US",
            has_catalog=True,
            limit=10,
        )

        request = route.calls.last.request
        assert "capabilities" in str(request.url)
        assert "industry=retail" in str(request.url)
        assert "region=US" in str(request.url)
        assert "has_catalog=true" in str(request.url).lower()
        assert "limit=10" in str(request.url)
        await http_client.close()

    @respx.mock
    async def test_get_merchant(self):
        """Test get merchant by domain."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        merchant_client = MerchantClient(http_client)

        response_data = {
            "domain": "shop.example.com",
            "name": "Example Shop",
            "description": "A premium retail shop",
            "ucp_profile": {"version": "1.0", "services": []},
            "capabilities": ["dev.ucp.shopping.checkout"],
            "endpoints": {
                "rest": "https://shop.example.com/ucp/v1",
                "mcp": "https://shop.example.com/ucp/mcp",
                "a2a": None,
            },
            "industry": "retail",
            "region": "US",
            "is_verified": True,
            "is_active": True,
            "first_discovered_at": "2024-01-01T00:00:00Z",
            "last_crawled_at": "2024-01-15T00:00:00Z",
            "search_appearances": 100,
            "click_count": 25,
        }

        respx.get("https://api.test.com/ucp/v1/merchants/shop.example.com").mock(
            return_value=Response(200, json=response_data)
        )

        result = await merchant_client.get("shop.example.com")

        assert result.domain == "shop.example.com"
        assert result.name == "Example Shop"
        await http_client.close()

    @respx.mock
    async def test_search_iter(self):
        """Test merchant search with auto-pagination."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        merchant_client = MerchantClient(http_client)

        page1 = {
            "merchants": [
                {
                    "id": 1,
                    "domain": "shop1.example.com",
                    "name": "Shop 1",
                    "industry": "retail",
                    "region": "US",
                    "capabilities": [],
                    "has_native_catalog": True,
                    "endpoints": {
                        "rest": "https://shop1.example.com/ucp/v1",
                        "mcp": None,
                        "a2a": None,
                    },
                    "ucp_profile_url": "https://shop1.example.com/.well-known/ucp",
                }
            ],
            "total": 2,
            "has_more": True,
            "limit": 1,
            "offset": 0,
            "session_id": "sess_123",
            "search_log_id": 456,
        }

        page2 = {
            "merchants": [
                {
                    "id": 2,
                    "domain": "shop2.example.com",
                    "name": "Shop 2",
                    "industry": "retail",
                    "region": "US",
                    "capabilities": [],
                    "has_native_catalog": False,
                    "endpoints": {
                        "rest": "https://shop2.example.com/ucp/v1",
                        "mcp": None,
                        "a2a": None,
                    },
                    "ucp_profile_url": "https://shop2.example.com/.well-known/ucp",
                }
            ],
            "total": 2,
            "has_more": False,
            "limit": 1,
            "offset": 1,
            "session_id": "sess_123",
            "search_log_id": 456,
        }

        route = respx.get("https://api.test.com/ucp/v1/merchants")
        route.side_effect = [
            Response(200, json=page1),
            Response(200, json=page2),
        ]

        merchants = []
        async for merchant in merchant_client.search_iter(industry="retail", limit=1):
            merchants.append(merchant)

        assert len(merchants) == 2
        assert merchants[0].domain == "shop1.example.com"
        assert merchants[1].domain == "shop2.example.com"
        await http_client.close()


@pytest.mark.unit
@pytest.mark.asyncio
class TestProductClient:
    """Test suite for ProductClient."""

    @respx.mock
    async def test_search_basic(self):
        """Test basic product search."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        product_client = ProductClient(http_client)

        response_data = {
            "products": [
                {
                    "id": 123,
                    "merchant_id": 1,
                    "merchant_domain": "shop.example.com",
                    "merchant_name": "Example Shop",
                    "title": "Laptop",
                    "description": "High-performance laptop",
                    "price": {"amount": 150000, "currency": "USD"},
                    "image_url": "https://shop.example.com/laptop.jpg",
                    "product_url": "https://shop.example.com/products/laptop",
                    "ucp_checkout_available": True,
                    "data_source": "ucp_catalog",
                    "quality_score": 95,
                }
            ],
            "total": 1,
            "has_more": False,
            "limit": 20,
            "offset": 0,
            "query": "laptop",
            "session_id": "sess_123",
            "search_log_id": 789,
        }

        respx.get("https://api.test.com/ucp/v1/products/search").mock(
            return_value=Response(200, json=response_data)
        )

        result = await product_client.search("laptop")

        assert len(result.products) == 1
        assert result.products[0].title == "Laptop"
        assert result.products[0].price.amount == 150000
        assert result.query == "laptop"
        await http_client.close()

    @respx.mock
    async def test_search_with_filters(self):
        """Test product search with price and category filters."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        product_client = ProductClient(http_client)

        response_data = {
            "products": [],
            "total": 0,
            "has_more": False,
            "limit": 20,
            "offset": 0,
            "query": "laptop",
            "session_id": "sess_123",
            "search_log_id": 789,
        }

        route = respx.get("https://api.test.com/ucp/v1/products/search").mock(
            return_value=Response(200, json=response_data)
        )

        await product_client.search(
            "laptop",
            price_min=50000,
            price_max=150000,
            category="electronics",
            brand="TechBrand",
            condition="new",
        )

        request = route.calls.last.request
        assert "q=laptop" in str(request.url)
        assert "price_min=50000" in str(request.url)
        assert "price_max=150000" in str(request.url)
        assert "category=electronics" in str(request.url)
        assert "brand=TechBrand" in str(request.url)
        assert "condition=new" in str(request.url)
        await http_client.close()

    @respx.mock
    async def test_search_iter(self):
        """Test product search with auto-pagination."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        product_client = ProductClient(http_client)

        page1 = {
            "products": [
                {
                    "id": 1,
                    "merchant_id": 1,
                    "merchant_domain": "shop.example.com",
                    "title": "Product 1",
                    "price": {"amount": 10000, "currency": "USD"},
                    "product_url": "https://shop.example.com/prod1",
                    "ucp_checkout_available": True,
                    "data_source": "ucp_catalog",
                    "quality_score": 90,
                }
            ],
            "total": 2,
            "has_more": True,
            "limit": 1,
            "offset": 0,
            "query": "test",
            "session_id": "sess_123",
            "search_log_id": 789,
        }

        page2 = {
            "products": [
                {
                    "id": 2,
                    "merchant_id": 1,
                    "merchant_domain": "shop.example.com",
                    "title": "Product 2",
                    "price": {"amount": 20000, "currency": "USD"},
                    "product_url": "https://shop.example.com/prod2",
                    "ucp_checkout_available": True,
                    "data_source": "ucp_catalog",
                    "quality_score": 85,
                }
            ],
            "total": 2,
            "has_more": False,
            "limit": 1,
            "offset": 1,
            "query": "test",
            "session_id": "sess_123",
            "search_log_id": 789,
        }

        route = respx.get("https://api.test.com/ucp/v1/products/search")
        route.side_effect = [
            Response(200, json=page1),
            Response(200, json=page2),
        ]

        products = []
        async for product in product_client.search_iter("test", limit=1):
            products.append(product)

        assert len(products) == 2
        assert products[0].id == 1
        assert products[1].id == 2
        await http_client.close()


@pytest.mark.unit
@pytest.mark.asyncio
class TestAnalyticsClient:
    """Test suite for AnalyticsClient."""

    @respx.mock
    async def test_log_click_product(self):
        """Test logging click on a product."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        analytics_client = AnalyticsClient(http_client)

        route = respx.post("https://api.test.com/ucp/v1/analytics/click").mock(
            return_value=Response(200, json={})
        )

        await analytics_client.log_click(
            search_log_id=789,
            clicked_product_id=123,
            clicked_position=0,
        )

        assert route.called
        await http_client.close()

    @respx.mock
    async def test_log_click_merchant(self):
        """Test logging click on a merchant."""
        http_client = HTTPClient(api_key="test_key", base_url="https://api.test.com")
        analytics_client = AnalyticsClient(http_client)

        route = respx.post("https://api.test.com/ucp/v1/analytics/click").mock(
            return_value=Response(200, json={})
        )

        await analytics_client.log_click(
            search_log_id=456,
            clicked_merchant_id=1,
            clicked_position=2,
        )

        assert route.called
        await http_client.close()


@pytest.mark.unit
@pytest.mark.asyncio
class TestUCPNamespace:
    """Test suite for UCPNamespace."""

    def test_namespace_initialization(self):
        """Test UCPNamespace initializes all clients."""
        http_client = HTTPClient(api_key="test_key")
        ucp = UCPNamespace(http_client)

        assert isinstance(ucp.merchants, MerchantClient)
        assert isinstance(ucp.products, ProductClient)
        assert isinstance(ucp.analytics, AnalyticsClient)

    @respx.mock
    async def test_namespace_via_main_client(self):
        """Test UCP access through main AsyncRencomClient."""
        response_data = {
            "merchants": [],
            "total": 0,
            "has_more": False,
            "limit": 20,
            "offset": 0,
            "session_id": "sess_123",
            "search_log_id": 456,
        }

        respx.get("https://api.test.com/ucp/v1/merchants").mock(
            return_value=Response(200, json=response_data)
        )

        async with AsyncRencomClient(api_key="test_key", base_url="https://api.test.com") as client:
            result = await client.ucp.merchants.search(industry="retail")
            assert len(result.merchants) == 0
