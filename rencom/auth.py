"""Authentication and account management client.

This module handles:
- Magic link authentication (passwordless)
- JWT token management
- API key CRUD operations
- Usage statistics
"""

import asyncio
from collections.abc import Coroutine
from typing import Any, TypeVar

from rencom._generated.models import (
    ApiKeyListItem,
    ApiKeyResponse,
    CreateApiKeyRequest,
    LoginRequest,
    LoginResponse,
    UsageResponse,
    UserResponse,
    VerifyResponse,
)
from rencom._http import HTTPClient

T = TypeVar("T")


class AuthClient:
    """Client for authentication and account management.

    Provides methods for:
    - Passwordless authentication via magic links
    - API key management (create, list, revoke)
    - User profile access
    - Usage statistics

    Example:
        >>> # Request magic link
        >>> await client.auth.request_magic_link("user@example.com")
        >>>
        >>> # Verify and get JWT
        >>> verify_result = await client.auth.verify_magic_link(token="...")
        >>> jwt = verify_result.access_token
        >>>
        >>> # Use JWT for authenticated requests
        >>> client = AsyncRencomClient(jwt_token=jwt)
        >>> user = await client.auth.me()
        >>> print(user.email)
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the auth client."""
        self._http = http_client

    async def request_magic_link(self, email: str) -> LoginResponse:
        """Request a magic link for passwordless authentication.

        Sends a magic link to the specified email address. The user
        clicks the link to verify their email and receive a JWT token.

        Args:
            email: Email address to send the magic link to

        Returns:
            LoginResponse with confirmation message

        Raises:
            ValidationError: If email format is invalid
            RateLimitError: If too many requests from this IP

        Example:
            >>> response = await client.auth.request_magic_link("user@example.com")
            >>> print(response.message)
            >>> # User clicks link in email and is redirected to frontend
        """
        request = LoginRequest(email=email)
        response_data = await self._http.post("/auth/login", json=request.model_dump())
        return LoginResponse.model_validate(response_data)

    async def verify_magic_link(self, token: str) -> VerifyResponse:
        """Verify a magic link token and get JWT.

        After the user clicks the magic link, this verifies the token
        and returns a JWT that can be used for authenticated requests.

        Args:
            token: Token from the magic link URL

        Returns:
            VerifyResponse containing access_token (JWT), user info, and default API key

        Raises:
            AuthenticationError: If token is invalid or expired

        Example:
            >>> verify_result = await client.auth.verify_magic_link(token="abc123")
            >>> jwt = verify_result.access_token
            >>> # Use JWT for subsequent requests
            >>> authed_client = AsyncRencomClient(jwt_token=jwt)
        """
        response_data = await self._http.get("/auth/verify", params={"token": token})
        return VerifyResponse.model_validate(response_data)

    async def me(self) -> UserResponse:
        """Get the current user's profile.

        Requires JWT authentication. Returns user information including
        email, verification status, and creation date.

        Returns:
            UserResponse object with profile information

        Raises:
            AuthenticationError: If JWT is invalid or expired

        Example:
            >>> user = await client.auth.me()
            >>> print(f"Email: {user.email}")
            >>> print(f"Verified: {user.email_verified}")
        """
        response_data = await self._http.get("/auth/me")
        return UserResponse.model_validate(response_data)

    async def list_api_keys(self) -> list[ApiKeyListItem]:
        """List all API keys for the current user.

        Requires JWT authentication. Returns all API keys created by
        the user, including key prefix, organization name, and usage stats.

        Returns:
            List of ApiKeyListItem objects

        Raises:
            AuthenticationError: If JWT is invalid

        Example:
            >>> keys = await client.auth.list_api_keys()
            >>> for key in keys:
            ...     print(f"{key.key_prefix}: {key.organization_name}")
            ...     print(f"  Requests: {key.requests_count}")
            ...     print(f"  Last used: {key.last_used_at}")
        """
        response_data = await self._http.get("/auth/api-keys")
        return [ApiKeyListItem.model_validate(item) for item in response_data]

    async def create_api_key(self, organization_name: str) -> ApiKeyResponse:
        """Create a new API key.

        Requires JWT authentication. Creates a new API key for the
        specified organization. The full key is only returned once during creation.

        Args:
            organization_name: Organization name for the API key

        Returns:
            ApiKeyResponse object with full key (only time it's visible)

        Raises:
            AuthenticationError: If JWT is invalid
            ValidationError: If organization_name is invalid

        Example:
            >>> key = await client.auth.create_api_key("Production App")
            >>> print(f"Save this key: {key.api_key}")
            >>> print(f"Rate limits: {key.rate_limit_per_minute}/min, {key.rate_limit_per_day}/day")
            >>> # Key will be like: rk_live_abc123xyz...
        """
        request = CreateApiKeyRequest(organization_name=organization_name)
        response_data = await self._http.post("/auth/api-keys", json=request.model_dump())
        return ApiKeyResponse.model_validate(response_data)

    async def delete_api_key(self, key_prefix: str) -> None:
        """Revoke an API key.

        Requires JWT authentication. Permanently revokes the specified
        API key. The key will no longer work for authentication.

        Args:
            key_prefix: Key prefix (e.g., "rk_live_abc123")

        Raises:
            AuthenticationError: If JWT is invalid
            NotFoundError: If key doesn't exist or doesn't belong to user

        Example:
            >>> await client.auth.delete_api_key("rk_live_abc123")
        """
        await self._http.delete(f"/auth/api-keys/{key_prefix}")

    async def usage(self) -> UsageResponse:
        """Get usage statistics for the current user.

        Requires JWT or API key authentication. Returns usage stats
        including total requests and per-key breakdowns.

        Returns:
            UsageResponse object with statistics

        Raises:
            AuthenticationError: If not authenticated

        Example:
            >>> usage = await client.auth.usage()
            >>> print(f"Total requests: {usage.total_requests}")
            >>> print(f"Current period: {usage.current_period}")
            >>> for key_usage in usage.api_keys:
            ...     print(f"Key {key_usage['key_prefix']}: {key_usage['requests']} requests")
        """
        response_data = await self._http.get("/auth/usage")
        return UsageResponse.model_validate(response_data)


class SyncAuthClient:
    """Synchronous wrapper for AuthClient.

    Provides a synchronous interface for authentication operations.
    """

    def __init__(
        self, async_client: AuthClient, loop: asyncio.AbstractEventLoop | None = None
    ) -> None:
        """Initialize sync wrapper.

        Args:
            async_client: Async AuthClient to wrap
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

    def request_magic_link(self, email: str) -> LoginResponse:
        """Synchronous version of request_magic_link()."""
        return self._run(self._async_client.request_magic_link(email))

    def verify_magic_link(self, token: str) -> VerifyResponse:
        """Synchronous version of verify_magic_link()."""
        return self._run(self._async_client.verify_magic_link(token))

    def me(self) -> UserResponse:
        """Synchronous version of me()."""
        return self._run(self._async_client.me())

    def list_api_keys(self) -> list[ApiKeyListItem]:
        """Synchronous version of list_api_keys()."""
        return self._run(self._async_client.list_api_keys())

    def create_api_key(self, organization_name: str) -> ApiKeyResponse:
        """Synchronous version of create_api_key()."""
        return self._run(self._async_client.create_api_key(organization_name))

    def delete_api_key(self, key_prefix: str) -> None:
        """Synchronous version of delete_api_key()."""
        return self._run(self._async_client.delete_api_key(key_prefix))

    def usage(self) -> UsageResponse:
        """Synchronous version of usage()."""
        return self._run(self._async_client.usage())
