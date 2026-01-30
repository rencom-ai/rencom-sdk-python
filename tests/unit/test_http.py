"""Unit tests for the HTTP client."""

import pytest
import respx
from httpx import Response

from rencom._http import HTTPClient
from rencom.exceptions import (
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ServiceUnavailableError,
    ValidationError,
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestHTTPClient:
    """Test suite for HTTPClient."""

    async def test_init_with_api_key(self):
        """Test HTTPClient initialization with API key."""
        client = HTTPClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.jwt_token is None
        assert client.admin_key is None
        await client.close()

    async def test_init_with_jwt_token(self):
        """Test HTTPClient initialization with JWT token."""
        client = HTTPClient(jwt_token="test_token")
        assert client.jwt_token == "test_token"
        assert client.api_key is None
        await client.close()

    async def test_build_headers_api_key(self):
        """Test header building with API key."""
        client = HTTPClient(api_key="test_key")
        headers = client._build_headers()
        assert headers["X-API-Key"] == "test_key"
        assert "Authorization" not in headers
        await client.close()

    async def test_build_headers_jwt(self):
        """Test header building with JWT token."""
        client = HTTPClient(jwt_token="test_token")
        headers = client._build_headers()
        assert headers["Authorization"] == "Bearer test_token"
        assert "X-API-Key" not in headers
        await client.close()

    async def test_build_headers_priority(self):
        """Test auth header priority: admin_key > jwt > api_key."""
        client = HTTPClient(api_key="api_key", jwt_token="jwt_token", admin_key="admin_key")
        headers = client._build_headers()
        assert headers["X-Admin-Key"] == "admin_key"
        assert "Authorization" not in headers
        assert "X-API-Key" not in headers
        await client.close()

    @respx.mock
    async def test_successful_get_request(self):
        """Test successful GET request."""
        client = HTTPClient(api_key="test_key", base_url="https://api.test.com")

        # Mock the response
        respx.get("https://api.test.com/test").mock(
            return_value=Response(200, json={"success": True})
        )

        result = await client.get("/test")
        assert result == {"success": True}
        await client.close()

    @respx.mock
    async def test_successful_post_request(self):
        """Test successful POST request."""
        client = HTTPClient(api_key="test_key", base_url="https://api.test.com")

        respx.post("https://api.test.com/test").mock(
            return_value=Response(200, json={"created": True})
        )

        result = await client.post("/test", json={"data": "value"})
        assert result == {"created": True}
        await client.close()

    @respx.mock
    async def test_validation_error_400(self):
        """Test ValidationError is raised on 400."""
        client = HTTPClient(api_key="test_key", base_url="https://api.test.com")

        respx.get("https://api.test.com/test").mock(
            return_value=Response(
                400, json={"detail": "Invalid input", "errors": [{"field": "query"}]}
            )
        )

        with pytest.raises(ValidationError) as exc_info:
            await client.get("/test")

        assert "Invalid input" in str(exc_info.value)
        assert exc_info.value.errors == [{"field": "query"}]
        await client.close()

    @respx.mock
    async def test_authentication_error_401(self):
        """Test AuthenticationError is raised on 401."""
        client = HTTPClient(api_key="test_key", base_url="https://api.test.com")

        respx.get("https://api.test.com/test").mock(
            return_value=Response(401, json={"detail": "Invalid API key"})
        )

        with pytest.raises(AuthenticationError) as exc_info:
            await client.get("/test")

        assert "Invalid API key" in str(exc_info.value)
        await client.close()

    @respx.mock
    async def test_authorization_error_403(self):
        """Test AuthorizationError is raised on 403."""
        client = HTTPClient(api_key="test_key", base_url="https://api.test.com")

        respx.get("https://api.test.com/test").mock(
            return_value=Response(403, json={"detail": "Forbidden"})
        )

        with pytest.raises(AuthorizationError):
            await client.get("/test")

        await client.close()

    @respx.mock
    async def test_not_found_error_404(self):
        """Test NotFoundError is raised on 404."""
        client = HTTPClient(api_key="test_key", base_url="https://api.test.com")

        respx.get("https://api.test.com/test").mock(
            return_value=Response(404, json={"detail": "Not found"})
        )

        with pytest.raises(NotFoundError):
            await client.get("/test")

        await client.close()

    @respx.mock
    async def test_rate_limit_error_429(self):
        """Test RateLimitError is raised on 429."""
        client = HTTPClient(api_key="test_key", base_url="https://api.test.com")

        respx.get("https://api.test.com/test").mock(
            return_value=Response(
                429,
                json={"detail": "Rate limit exceeded"},
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit-Minute": "100",
                    "X-RateLimit-Remaining-Minute": "0",
                },
            )
        )

        with pytest.raises(RateLimitError) as exc_info:
            await client.get("/test")

        assert exc_info.value.retry_after == 60
        assert exc_info.value.limit == 100
        assert exc_info.value.remaining == 0
        await client.close()

    @respx.mock
    async def test_server_error_500(self):
        """Test ServerError is raised on 500."""
        client = HTTPClient(api_key="test_key", base_url="https://api.test.com")

        respx.get("https://api.test.com/test").mock(
            return_value=Response(500, json={"detail": "Internal server error"})
        )

        with pytest.raises(ServerError):
            await client.get("/test")

        await client.close()

    @respx.mock
    async def test_service_unavailable_error_503(self):
        """Test ServiceUnavailableError is raised on 503."""
        client = HTTPClient(api_key="test_key", base_url="https://api.test.com")

        respx.get("https://api.test.com/test").mock(
            return_value=Response(503, json={"detail": "Service unavailable"})
        )

        with pytest.raises(ServiceUnavailableError):
            await client.get("/test")

        await client.close()

    @respx.mock
    async def test_retry_on_500(self):
        """Test retry logic on 500 errors."""
        client = HTTPClient(api_key="test_key", base_url="https://api.test.com", max_retries=2)

        # First two attempts fail, third succeeds
        route = respx.get("https://api.test.com/test")
        route.side_effect = [
            Response(500, json={"detail": "Error"}),
            Response(500, json={"detail": "Error"}),
            Response(200, json={"success": True}),
        ]

        result = await client.get("/test")
        assert result == {"success": True}
        assert route.call_count == 3
        await client.close()

    @respx.mock
    async def test_max_retries_exceeded(self):
        """Test that max retries are respected."""
        client = HTTPClient(api_key="test_key", base_url="https://api.test.com", max_retries=2)

        # All attempts fail
        route = respx.get("https://api.test.com/test")
        route.mock(return_value=Response(500, json={"detail": "Error"}))

        with pytest.raises(ServerError):
            await client.get("/test")

        # Should be 1 initial + 2 retries = 3 total
        assert route.call_count == 3
        await client.close()

    def test_parse_rate_limit_headers(self):
        """Test rate limit header parsing."""
        client = HTTPClient(api_key="test_key")

        headers = {
            "X-RateLimit-Limit-Minute": "100",
            "X-RateLimit-Remaining-Minute": "95",
            "X-RateLimit-Limit-Daily": "10000",
            "X-RateLimit-Remaining-Daily": "9500",
            "X-RateLimit-Reset": "1234567890",
        }

        info = client._parse_rate_limit_headers(headers)
        assert info["limit_minute"] == 100
        assert info["remaining_minute"] == 95
        assert info["limit_daily"] == 10000
        assert info["remaining_daily"] == 9500
        assert info["reset_at"] == 1234567890

    def test_parse_rate_limit_headers_partial(self):
        """Test rate limit header parsing with missing headers."""
        client = HTTPClient(api_key="test_key")

        headers = {"X-RateLimit-Limit-Minute": "100"}

        info = client._parse_rate_limit_headers(headers)
        assert info["limit_minute"] == 100
        assert "remaining_minute" not in info
