"""Pytest configuration and shared fixtures."""

import os
from collections.abc import AsyncIterator

import pytest

from rencom import AsyncRencomClient


@pytest.fixture
def api_key() -> str:
    """Get API key from environment for integration tests."""
    key = os.getenv("RENCOM_API_KEY")
    if not key:
        pytest.skip("RENCOM_API_KEY not set")
    return key


@pytest.fixture
async def client(api_key: str) -> AsyncIterator[AsyncRencomClient]:
    """Create an async client for integration tests."""
    async with AsyncRencomClient(api_key=api_key, base_url="http://localhost:8080") as client:
        yield client


@pytest.fixture
def sample_search_response() -> dict:
    """Sample search response for testing."""
    return {
        "results": [
            {
                "id": 123,
                "resource": "https://api.example.com/v1/trading",
                "description": "Real-time trading data API",
                "max_amount_required": 1000000,
                "network": "base",
                "final_score": 0.92,
            }
        ],
        "has_more": False,
        "limit": 3,
        "offset": 0,
        "query": "trading api",
        "sort_by": "recommended",
    }


@pytest.fixture
def sample_merchant_response() -> dict:
    """Sample merchant response for testing."""
    return {
        "results": [
            {
                "id": 1,
                "domain": "example.com",
                "name": "Example Store",
                "industry": "retail",
                "region": "US",
                "capabilities": ["dev.ucp.shopping.checkout"],
                "has_native_catalog": True,
            }
        ],
        "total": 1,
        "limit": 20,
        "offset": 0,
    }


@pytest.fixture
def sample_product_response() -> dict:
    """Sample product response for testing."""
    return {
        "results": [
            {
                "id": "prod_123",
                "name": "Laptop",
                "description": "High-performance laptop",
                "price_cents": 150000,
                "currency": "USD",
                "merchant_domain": "example.com",
                "category": "electronics",
                "brand": "TechBrand",
                "condition": "new",
            }
        ],
        "total": 1,
        "limit": 20,
        "offset": 0,
    }
