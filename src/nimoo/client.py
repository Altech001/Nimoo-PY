from __future__ import annotations

import re
from typing import Any

# pyrefly: ignore [missing-import]
import httpx

from nimoo.exceptions import InvalidPhoneNumberError, NetworkError, NimoAPIError
from nimoo.models import VerificationResult

DEFAULT_BASE_URL = "https://nimo.renult.xyz"
DEFAULT_TIMEOUT = 15.0
VERIFY_PATH = "/api/v1/phone-msisdn/verify"

_HEADERS = {"accept": "application/json"}


_SEPARATORS = str.maketrans("", "", " -.()")
_PHONE_PATTERN = re.compile(r"\+?\d+", re.ASCII)


def normalize_phone_number(phone_number: str) -> str:

    normalized = phone_number.translate(_SEPARATORS)
    if not _PHONE_PATTERN.fullmatch(normalized):
        raise InvalidPhoneNumberError(
            phone_number, "must contain digits only (optionally prefixed with '+')"
        )
    return normalized


def _extract_detail(response: httpx.Response) -> str:
    try:
        payload: Any = response.json()
    except ValueError:
        payload = None
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
        if isinstance(detail, list):
            parts = []
            for item in detail:
                if isinstance(item, dict):
                    loc = ".".join(str(part) for part in item.get("loc", ()))
                    msg = item.get("msg", "invalid value")
                    parts.append(f"{loc}: {msg}" if loc else str(msg))
                else:
                    parts.append(str(item))
            if parts:
                return "; ".join(parts)
    return (response.text or "no response body").strip()


def _parse_response(response: httpx.Response, phone_number: str) -> VerificationResult:
    if response.status_code == 200:
        try:
            payload: Any = response.json()
        except ValueError as exc:
            raise NimoAPIError(
                "Nimo API returned malformed JSON",
                status_code=response.status_code,
                response_body=response.text,
            ) from exc
        if not isinstance(payload, dict):
            raise NimoAPIError(
                f"Nimo API returned an unexpected response body: {response.text!r}",
                status_code=response.status_code,
                response_body=response.text,
            )
        return VerificationResult.from_api(payload)

    detail = _extract_detail(response)
    if response.status_code == 422:
        raise InvalidPhoneNumberError(phone_number, detail)
    raise NimoAPIError(
        f"Nimo API request failed with status {response.status_code}: {detail}",
        status_code=response.status_code,
        response_body=response.text,
    )


class NimoClient:
    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float | httpx.Timeout = DEFAULT_TIMEOUT,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._client = http_client or httpx.Client(base_url=base_url, timeout=timeout)
        self._owns_client = http_client is None

    def verify(self, phone_number: str) -> VerificationResult:
        normalized = normalize_phone_number(phone_number)
        try:
            response = self._client.post(
                VERIFY_PATH, json={"phone_number": normalized}, headers=_HEADERS
            )
        except httpx.HTTPError as exc:
            raise NetworkError(f"Request to the Nimo API failed: {exc}") from exc
        return _parse_response(response, phone_number)

    def close(self) -> None:
        """Close the underlying HTTP client if it is owned by this instance."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> NimoClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


class AsyncNimoClient:
    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float | httpx.Timeout = DEFAULT_TIMEOUT,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._client = http_client or httpx.AsyncClient(base_url=base_url, timeout=timeout)
        self._owns_client = http_client is None

    async def verify(self, phone_number: str) -> VerificationResult:
        normalized = normalize_phone_number(phone_number)
        try:
            response = await self._client.post(
                VERIFY_PATH, json={"phone_number": normalized}, headers=_HEADERS
            )
        except httpx.HTTPError as exc:
            raise NetworkError(f"Request to the Nimo API failed: {exc}") from exc
        return _parse_response(response, phone_number)

    async def close(self) -> None:
        """Close the underlying HTTP client if it is owned by this instance."""
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncNimoClient:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.close()


def verify(
    phone_number: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float | httpx.Timeout = DEFAULT_TIMEOUT,
) -> VerificationResult:
    with NimoClient(base_url=base_url, timeout=timeout) as client:
        return client.verify(phone_number)


async def averify(
    phone_number: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float | httpx.Timeout = DEFAULT_TIMEOUT,
) -> VerificationResult:
    async with AsyncNimoClient(base_url=base_url, timeout=timeout) as client:
        return await client.verify(phone_number)
