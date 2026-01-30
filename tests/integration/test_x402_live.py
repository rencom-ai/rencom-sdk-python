"""Integration tests for x402 search against live API."""

import pytest

# TODO: Import after implementation
# from rencom import AsyncRencomClient


@pytest.mark.integration
async def test_x402_search_live(client):
    """Test x402 search against live API."""
    # TODO: Implement
    # results = await client.x402.search("api")
    # assert len(results.results) > 0
    # assert results.results[0].resource.startswith("https://")
    pass


@pytest.mark.integration
async def test_x402_search_with_filters(client):
    """Test x402 search with sorting and limits."""
    # TODO: Implement
    # results = await client.x402.search("api", sort_by="price_low", limit=5)
    # assert len(results.results) <= 5
    # # Verify prices are sorted ascending
    pass


@pytest.mark.integration
async def test_x402_pagination(client):
    """Test x402 pagination."""
    # TODO: Implement
    # page1 = await client.x402.search("api", limit=3, offset=0)
    # page2 = await client.x402.search("api", limit=3, offset=3)
    # # Verify different results
    pass
