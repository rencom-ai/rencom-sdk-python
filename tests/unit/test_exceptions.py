"""Test exception classes."""

import pytest

from rencom.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    RencomError,
    ValidationError,
)


@pytest.mark.unit
def test_base_exception():
    """Test base RencomError."""
    error = RencomError("Something went wrong")
    assert str(error) == "Something went wrong"
    assert error.message == "Something went wrong"
    assert error.response is None


@pytest.mark.unit
def test_rate_limit_error():
    """Test RateLimitError with metadata."""
    error = RateLimitError(
        "Rate limit exceeded",
        retry_after=60,
        limit=100,
        remaining=0,
        reset_at=1234567890,
    )
    assert error.retry_after == 60
    assert error.limit == 100
    assert error.remaining == 0
    assert error.reset_at == 1234567890


@pytest.mark.unit
def test_validation_error():
    """Test ValidationError with field errors."""
    errors = [
        {"field": "query", "message": "Field required"},
        {"field": "limit", "message": "Must be between 1 and 5"},
    ]
    error = ValidationError("Validation failed", errors=errors)
    assert len(error.errors) == 2
    assert error.errors[0]["field"] == "query"


@pytest.mark.unit
def test_exception_inheritance():
    """Test that all exceptions inherit from RencomError."""
    assert issubclass(AuthenticationError, RencomError)
    assert issubclass(RateLimitError, RencomError)
    assert issubclass(ValidationError, RencomError)
    assert issubclass(NotFoundError, RencomError)
