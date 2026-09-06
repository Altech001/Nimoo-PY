"""Tests for nimoo clients, phone number normalization, and error handling."""

import json

import httpx
import pytest
import respx

from nimoo import (
    AsyncNimoClient,
    InvalidPhoneNumberError,
    NetworkError,
    NimoAPIError,
    NimoClient,
    VerificationResult,
    averify,
    verify,
)

BASE_URL = "https://nimo.renult.xyz"
VERIFY_URL = f"{BASE_URL}/api/v1/phone-msisdn/verify"
SUCCESS_BODY = {"msisdn": "256708215305", "status": "verified", "full_name": "ABAASA ALBERT"}


@pytest.mark.parametrize(
    ("raw", "normalized"),
    [
        ("256708215305", "256708215305"),
        ("+256708215305", "+256708215305"),
        ("+256 708 215 305", "+256708215305"),
        ("256-708-215-305", "256708215305"),
        ("(256) 708.215.305", "256708215305"),
        ("  256708215305  ", "256708215305"),
    ],
)
def test_phone_numbers_are_normalized(raw, normalized):
    with respx.mock:
        route = respx.post(VERIFY_URL).respond(200, json=SUCCESS_BODY)
        result = verify(raw)
        assert route.called
        assert json.loads(route.calls.last.request.content) == {"phone_number": normalized}
        assert result.msisdn == "256708215305"


@pytest.mark.parametrize(
    "bad", ["", "  ", "abc", "+", "256-70-abc", "2567082153o5", "25+6708215305", "١٢٣"]
)
def test_invalid_phone_numbers_raise_before_any_request(bad):
    with respx.mock:
        route = respx.post(VERIFY_URL).respond(200, json=SUCCESS_BODY)
        with pytest.raises(InvalidPhoneNumberError) as excinfo:
            verify(bad)
        assert not route.called
        assert "digits" in str(excinfo.value)


def test_verify_success():
    with respx.mock:
        respx.post(VERIFY_URL).respond(200, json=SUCCESS_BODY)
        result = verify("256708215305")
        assert result == VerificationResult(
            msisdn="256708215305", status="verified", full_name="ABAASA ALBERT"
        )
        assert result.is_verified


def test_verify_without_name():
    with respx.mock:
        respx.post(VERIFY_URL).respond(
            200, json={"msisdn": "256708215305", "status": "not_verified", "full_name": None}
        )
        result = verify("256708215305")
        assert result.full_name is None
        assert not result.is_verified


def test_request_headers_and_payload():
    with respx.mock:
        route = respx.post(VERIFY_URL).respond(200, json=SUCCESS_BODY)
        verify("256708215305")
        request = route.calls.last.request
        assert request.headers["accept"] == "application/json"
        assert request.headers["content-type"] == "application/json"
        assert json.loads(request.content) == {"phone_number": "256708215305"}


def test_api_validation_error_maps_to_invalid_phone_number():
    body = {
        "detail": [
            {
                "type": "value_error",
                "loc": ["body", "phone_number"],
                "msg": "Value error, phone_number must contain digits only"
                " (optionally prefixed with '+').",
                "input": "not-a-number",
            }
        ]
    }
    with respx.mock:
        respx.post(VERIFY_URL).respond(422, json=body)
        with pytest.raises(InvalidPhoneNumberError) as excinfo:
            verify("256708215305")
        assert "phone_number" in str(excinfo.value)
        assert "digits" in str(excinfo.value)


def test_service_error_maps_to_nimo_api_error():
    body = {"detail": "Phone verification service request failed: upstream error"}
    with respx.mock:
        respx.post(VERIFY_URL).respond(502, json=body)
        with pytest.raises(NimoAPIError) as excinfo:
            verify("256708215305")
        assert excinfo.value.status_code == 502
        assert "upstream error" in str(excinfo.value)
        assert excinfo.value.response_body


def test_malformed_success_body_maps_to_nimo_api_error():
    with respx.mock:
        respx.post(VERIFY_URL).respond(200, text="<html>gateway</html>")
        with pytest.raises(NimoAPIError):
            verify("256708215305")


def test_non_object_success_body_maps_to_nimo_api_error():
    with respx.mock:
        respx.post(VERIFY_URL).respond(200, json=["unexpected"])
        with pytest.raises(NimoAPIError):
            verify("256708215305")


def test_network_errors_are_wrapped():
    with respx.mock:
        respx.post(VERIFY_URL).mock(side_effect=httpx.ConnectError("no route to host"))
        with pytest.raises(NetworkError):
            verify("256708215305")


def test_client_reuse_for_multiple_numbers():
    with respx.mock:
        route = respx.post(VERIFY_URL).respond(200, json=SUCCESS_BODY)
        with NimoClient() as client:
            for _ in range(3):
                assert client.verify("256708215305").is_verified
        assert len(route.calls) == 3


def test_custom_base_url():
    url = "https://nimo.example.com/api/v1/phone-msisdn/verify"
    with respx.mock:
        route = respx.post(url).respond(200, json=SUCCESS_BODY)
        with NimoClient(base_url="https://nimo.example.com") as client:
            client.verify("256708215305")
        assert route.called


def test_injected_http_client_is_not_closed():
    with respx.mock:
        respx.post(VERIFY_URL).respond(200, json=SUCCESS_BODY)
        http_client = httpx.Client(base_url=BASE_URL)
        client = NimoClient(http_client=http_client)
        try:
            assert client.verify("256708215305").is_verified
            client.close()
            assert not http_client.is_closed
        finally:
            http_client.close()


async def test_async_verify_success():
    with respx.mock:
        route = respx.post(VERIFY_URL).respond(200, json=SUCCESS_BODY)
        result = await averify("256708215305")
        assert route.called
        assert result.is_verified
        assert result.full_name == "ABAASA ALBERT"


async def test_async_client_verify():
    with respx.mock:
        respx.post(VERIFY_URL).respond(200, json=SUCCESS_BODY)
        async with AsyncNimoClient() as client:
            result = await client.verify("+256 (708) 215-305")
        assert result.msisdn == "256708215305"
        assert result.is_verified


async def test_async_invalid_phone_number():
    with respx.mock:
        route = respx.post(VERIFY_URL).respond(200, json=SUCCESS_BODY)
        with pytest.raises(InvalidPhoneNumberError):
            await averify("abc")
        assert not route.called


async def test_async_network_errors_are_wrapped():
    with respx.mock:
        respx.post(VERIFY_URL).mock(side_effect=httpx.ConnectError("no route to host"))
        with pytest.raises(NetworkError):
            await averify("256708215305")
