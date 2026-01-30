"""Exception classes for the Rencom SDK.

All SDK-specific exceptions inherit from RencomError.
HTTP errors are mapped to domain-specific exceptions.
"""

from typing import Any


class RencomError(Exception):
    """Base exception for all Rencom SDK errors.

    All other exceptions inherit from this, allowing users to catch
    all SDK errors with a single except clause.

    Attributes:
        message: Error message
        response: Raw HTTP response if available
    """

    def __init__(self, message: str, response: Any | None = None) -> None:
        """Initialize the exception."""
        super().__init__(message)
        self.message = message
        self.response = response


class AuthenticationError(RencomError):
    """Authentication failed (HTTP 401).

    Raised when:
    - API key is invalid or expired
    - JWT token is invalid or expired
    - x402 payment verification fails

    Example:
        >>> try:
        ...     await client.x402.search("api")
        ... except AuthenticationError:
        ...     print("Invalid API key, please check your credentials")
    """

    pass


class AuthorizationError(RencomError):
    """Authorization failed (HTTP 403).

    Raised when the authenticated user doesn't have permission
    to access the requested resource.
    """

    pass


class NotFoundError(RencomError):
    """Resource not found (HTTP 404).

    Raised when the requested resource doesn't exist.
    """

    pass


class ValidationError(RencomError):
    """Request validation failed (HTTP 400).

    Raised when request parameters are invalid or missing.

    Attributes:
        errors: List of validation errors from the API
    """

    def __init__(
        self,
        message: str,
        errors: list[dict[str, Any]] | None = None,
        response: Any | None = None,
    ) -> None:
        """Initialize the validation error."""
        super().__init__(message, response)
        self.errors = errors or []


class RateLimitError(RencomError):
    """Rate limit exceeded (HTTP 429).

    Raised when API rate limits are exceeded.

    Attributes:
        retry_after: Seconds until the rate limit resets
        limit: Total rate limit
        remaining: Remaining requests before limit
        reset_at: Timestamp when the limit resets
    """

    def __init__(
        self,
        message: str,
        *,
        retry_after: int | None = None,
        limit: int | None = None,
        remaining: int | None = None,
        reset_at: int | None = None,
        response: Any | None = None,
    ) -> None:
        """Initialize the rate limit error."""
        super().__init__(message, response)
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining
        self.reset_at = reset_at


class ServerError(RencomError):
    """Server error (HTTP 5xx).

    Raised when the API returns a server error.
    """

    pass


class ServiceUnavailableError(ServerError):
    """Service temporarily unavailable (HTTP 503).

    Raised when the API is temporarily unavailable,
    often during maintenance or high load.
    """

    pass


class NetworkError(RencomError):
    """Network error occurred.

    Raised when a network-level error occurs (connection timeout,
    DNS failure, etc.) before receiving an HTTP response.
    """

    pass


class TimeoutError(NetworkError):
    """Request timeout.

    Raised when a request exceeds the configured timeout.
    """

    pass
