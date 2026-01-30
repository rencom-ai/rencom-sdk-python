"""Low-level HTTP client for making API requests.

This module handles:
- HTTP connection pooling
- Authentication (API key, JWT, Admin key)
- Rate limiting and retries
- Error handling and exception mapping
- Request/response logging
"""

import asyncio
import random
from typing import Any

import httpx

from rencom.exceptions import (
    AuthenticationError,
    AuthorizationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    RencomError,
    ServerError,
    ServiceUnavailableError,
    TimeoutError,
    ValidationError,
)


class HTTPClient:
    """Low-level HTTP client for Rencom API requests.

    This is an internal class that handles raw HTTP operations.
    Users should use AsyncRencomClient instead.

    Args:
        api_key: API key for X-API-Key header
        jwt_token: JWT token for Authorization header
        admin_key: Admin API key for X-Admin-Key header
        base_url: Base URL for all requests
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        auto_retry_rate_limits: Whether to retry on 429 errors

    Attributes:
        client: httpx.AsyncClient instance
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        jwt_token: str | None = None,
        admin_key: str | None = None,
        base_url: str = "https://api.rencom.ai",
        timeout: float = 30.0,
        max_retries: int = 3,
        auto_retry_rate_limits: bool = False,
    ) -> None:
        """Initialize the HTTP client."""
        self.api_key = api_key
        self.jwt_token = jwt_token
        self.admin_key = admin_key
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.auto_retry_rate_limits = auto_retry_rate_limits

        # Create httpx client with connection pooling and HTTP/2 support
        limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
        transport = httpx.AsyncHTTPTransport(http2=True, limits=limits)

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout),
            transport=transport,
            follow_redirects=True,
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            path: URL path (relative to base_url)
            params: Query parameters
            json: JSON request body
            headers: Additional headers

        Returns:
            Response JSON as dict

        Raises:
            AuthenticationError: On 401
            RateLimitError: On 429
            ValidationError: On 400
            NotFoundError: On 404
            ServerError: On 5xx
            NetworkError: On network failures
        """
        # Build headers with authentication
        request_headers = self._build_headers(headers)

        # Retry logic with exponential backoff
        last_exception: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.request(
                    method=method,
                    url=path,
                    params=params,
                    json=json,
                    headers=request_headers,
                )

                # Handle error responses
                if response.status_code >= 400:
                    await self._handle_error_response(response)

                # Parse and return JSON
                result: dict[str, Any] = response.json()
                return result

            except httpx.TimeoutException:
                last_exception = TimeoutError(
                    f"Request timeout after {self.client.timeout}s", response=None
                )
                if attempt < self.max_retries:
                    await self._wait_with_backoff(attempt)
                    continue
                raise last_exception from None

            except httpx.NetworkError as e:
                last_exception = NetworkError(f"Network error: {e}", response=None)
                if attempt < self.max_retries:
                    await self._wait_with_backoff(attempt)
                    continue
                raise last_exception from None

            except (ServerError, ServiceUnavailableError) as e:
                # Retry on server errors
                last_exception = e
                if attempt < self.max_retries:
                    await self._wait_with_backoff(attempt)
                    continue
                raise

            except RateLimitError as e:
                # Rate limit errors are handled specially
                if self.auto_retry_rate_limits and attempt < self.max_retries:
                    if e.retry_after:
                        await asyncio.sleep(e.retry_after)
                    else:
                        await self._wait_with_backoff(attempt)
                    continue
                raise

        # This should not be reached, but just in case
        if last_exception:
            raise last_exception
        raise RencomError("Request failed after all retry attempts")

    def _build_headers(self, extra_headers: dict[str, str] | None = None) -> dict[str, str]:
        """Build request headers with authentication.

        Auth priority: admin_key > jwt_token > api_key
        """
        headers = {"Content-Type": "application/json"}

        # Add authentication (priority order)
        if self.admin_key:
            headers["X-Admin-Key"] = self.admin_key
        elif self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        elif self.api_key:
            headers["X-API-Key"] = self.api_key

        # Add extra headers
        if extra_headers:
            headers.update(extra_headers)

        return headers

    async def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle HTTP error responses by raising appropriate exceptions."""
        status = response.status_code

        # Try to parse error message from response
        try:
            error_data = response.json()
            message = error_data.get("detail", response.text)
            errors = error_data.get("errors")
        except Exception:
            message = response.text or f"HTTP {status}"
            errors = None

        # Map status codes to exceptions
        if status == 400:
            raise ValidationError(message, errors=errors, response=response)

        elif status == 401:
            raise AuthenticationError(message, response=response)

        elif status == 403:
            raise AuthorizationError(message, response=response)

        elif status == 404:
            raise NotFoundError(message, response=response)

        elif status == 429:
            # Parse rate limit headers directly from response
            retry_after = int(response.headers.get("Retry-After", "60"))
            limit_minute = response.headers.get("X-RateLimit-Limit-Minute")
            remaining_minute = response.headers.get("X-RateLimit-Remaining-Minute")
            reset_at = response.headers.get("X-RateLimit-Reset")

            raise RateLimitError(
                message,
                retry_after=retry_after,
                limit=int(limit_minute) if limit_minute else None,
                remaining=int(remaining_minute) if remaining_minute else None,
                reset_at=int(reset_at) if reset_at else None,
                response=response,
            )

        elif status == 503:
            raise ServiceUnavailableError(message, response=response)

        elif status >= 500:
            raise ServerError(message, response=response)

        else:
            raise RencomError(f"HTTP {status}: {message}", response=response)

    def _parse_rate_limit_headers(self, headers: dict[str, str]) -> dict[str, Any]:
        """Parse rate limit information from response headers.

        Args:
            headers: Response headers

        Returns:
            Dict with rate limit info (limit, remaining, reset)
        """
        info: dict[str, Any] = {}

        # Parse minute rate limits
        if "X-RateLimit-Limit-Minute" in headers:
            info["limit_minute"] = int(headers["X-RateLimit-Limit-Minute"])
        if "X-RateLimit-Remaining-Minute" in headers:
            info["remaining_minute"] = int(headers["X-RateLimit-Remaining-Minute"])

        # Parse daily rate limits
        if "X-RateLimit-Limit-Daily" in headers:
            info["limit_daily"] = int(headers["X-RateLimit-Limit-Daily"])
        if "X-RateLimit-Remaining-Daily" in headers:
            info["remaining_daily"] = int(headers["X-RateLimit-Remaining-Daily"])

        # Parse reset timestamp
        if "X-RateLimit-Reset" in headers:
            info["reset_at"] = int(headers["X-RateLimit-Reset"])

        return info

    async def _wait_with_backoff(self, attempt: int) -> None:
        """Wait with exponential backoff and jitter.

        Base delay: 1s
        Max delay: 60s
        Jitter: ±25%
        """
        base_delay = 1.0
        max_delay = 60.0

        # Exponential backoff: 1s, 2s, 4s, 8s, ...
        delay = min(base_delay * (2**attempt), max_delay)

        # Add jitter (±25%)
        jitter = random.uniform(-0.25, 0.25) * delay
        delay += jitter

        await asyncio.sleep(max(0, delay))

    async def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a GET request."""
        return await self.request("GET", path, params=params, headers=headers)

    async def post(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request."""
        return await self.request("POST", path, json=json, headers=headers)

    async def delete(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a DELETE request."""
        return await self.request("DELETE", path, headers=headers)

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self.client.aclose()
