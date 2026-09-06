"""Response models for the Nimo phone verification API."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class VerificationResult:
    """The result of verifying a phone number.

    Attributes:
        msisdn: The verified phone number in MSISDN format (e.g. ``256708215305``).
        status: Verification status reported by the API (e.g. ``verified``).
        full_name: The full name registered to the number, if any.
    """

    msisdn: str
    status: str
    full_name: str | None = None

    @property
    def is_verified(self) -> bool:
        """Whether the phone number's status is ``verified``."""
        return self.status == "verified"

    @classmethod
    def from_api(cls, payload: Mapping[str, Any]) -> VerificationResult:
        """Build a result from the JSON payload of a successful API response."""
        return cls(
            msisdn=str(payload.get("msisdn", "")),
            status=str(payload.get("status", "")),
            full_name=payload.get("full_name"),
        )
