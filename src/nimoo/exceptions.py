"""Exceptions raised by nimoo."""


class NimoError(Exception):
    """Base class for all nimoo errors."""


class InvalidPhoneNumberError(NimoError):
    """Raised when a phone number is not digits (optionally prefixed with ``+``)."""

    def __init__(self, phone_number: str, reason: str) -> None:
        self.phone_number = phone_number
        self.reason = reason
        super().__init__(f"Invalid phone number {phone_number!r}: {reason}")


class NimoAPIError(NimoError):
    """Raised when the Nimo API returns an unexpected error response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class NetworkError(NimoError):
    """Raised when the request to the Nimo API fails at the transport level."""
