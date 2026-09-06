"""nimoo — phone number verification via the Nimo API."""

from nimoo.client import AsyncNimoClient, NimoClient, averify, verify
from nimoo.exceptions import (
    InvalidPhoneNumberError,
    NetworkError,
    NimoAPIError,
    NimoError,
)
from nimoo.models import VerificationResult

__version__ = "0.1.0"

__all__ = [
    "AsyncNimoClient",
    "InvalidPhoneNumberError",
    "NetworkError",
    "NimoAPIError",
    "NimoClient",
    "NimoError",
    "VerificationResult",
    "averify",
    "verify",
]
