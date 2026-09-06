"""Live tests that hit the real Nimo API.

Deselected by default; run with ``uv run pytest -m live``.
"""

import pytest

from nimoo import averify, verify

pytestmark = pytest.mark.live

KNOWN_VERIFIED = "256708215305"


def test_verify_known_number():
    result = verify(KNOWN_VERIFIED)
    assert result.msisdn == KNOWN_VERIFIED
    assert result.status == "verified"
    assert result.full_name


async def test_averify_known_number():
    result = await averify(KNOWN_VERIFIED)
    assert result.is_verified
