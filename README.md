<div align="center">

## Nimo SDK
>>> Verify Ugandan phone numbers (MSISDN) in seconds.
</div>

#### Author
>> Github [@Altech001](https://github.com/Altech001)


[![npm](https://img.shields.io/npm/v/nimo)](https://npmjs.com/package/nimo)
[![license](https://img.shields.io/npm/l/nimo)](LICENSE)



Phone number verification via the [Nimo API](https://nimo.xyz).
Give it a phone number; it tells you whether the number is verified and the
full name registered to it.

- Single-purpose: phone number verification, nothing else
- Sync and async, first-class (`httpx` under the hood)
- Fully typed, with one exception per failure mode
- Accepts human-friendly input (`+256 708-215.305`) and normalizes it

## Installation

```bash
uv add nimoo        # or: pip install nimoo
```

From this checkout:

```bash
uv pip install .
```

## Quickstart

One-shot verification:

```python
from nimoo import verify

result = verify("256708215305")
print(result.msisdn)  # "256708215305"
print(result.status)  # "verified"
print(result.full_name)  # "ABAASA ALBERT"
print(result.is_verified)  # True
```

Reuse a client when verifying many numbers:

```python
from nimoo import NimoClient

with NimoClient() as client:
    result = client.verify("+256 (708) 215-305")
```

Async:

```python
import asyncio

from nimoo import averify, AsyncNimoClient


async def main():
    result = await averify("256708215305")

    # or, reused:
    async with AsyncNimoClient() as client:
        results = await asyncio.gather(
            client.verify("256708215305"),
            client.verify("256770000000"),
        )


asyncio.run(main())
```

From the command line:

```bash
uv run examples/verify.py 256708215305
```

## The result

`verify(...)` returns an immutable `VerificationResult`:

| Field        | Type           | Description                                        |
| ------------ | -------------- | -------------------------------------------------- |
| `msisdn`     | `str`          | The phone number in MSISDN format                  |
| `status`     | `str`          | Verification status, e.g. `"verified"`             |
| `full_name`  | `str \| None`  | Full name registered to the number, if any         |
| `is_verified`| `bool`         | Convenience property: `status == "verified"`       |

## Error handling

All exceptions derive from `nimoo.NimoError`:

| Exception                  | Raised when                                                |
| -------------------------- | ---------------------------------------------------------- |
| `InvalidPhoneNumberError`  | The number isn't digits (optionally prefixed with `+`). Raised client-side, or on the API's `422`. |
| `NimoAPIError`             | The API returned an unexpected error (e.g. `502` upstream failure). Carries `status_code` and `response_body`. |
| `NetworkError`             | The request failed at the transport level (DNS, connection, timeout). |

```python
from nimoo import InvalidPhoneNumberError, NetworkError, NimoAPIError, verify

try:
    result = verify("256708215305")
except InvalidPhoneNumberError as exc:
    print(f"bad input: {exc}")
except NimoAPIError as exc:
    print(f"API error (HTTP {exc.status_code}): {exc}")
except NetworkError as exc:
    print(f"network problem: {exc}")
```

## Configuration

`NimoClient` / `AsyncNimoClient` accept:

- `base_url` — API base URL (default `https://nimo.xyz`)
- `timeout` — request timeout in seconds (default `15`)
- `http_client` — an `httpx.Client` / `httpx.AsyncClient` you own (proxies,
  custom transports, shared connection pools). Injected clients are never
  closed by nimoo.

The one-shot `verify()` / `averify()` functions accept `base_url` and `timeout`.

## Development

```bash
uv sync                  # install package + dev tools
uv run pytest            # mocked test suite (no network)
uv run pytest -m live    # live tests against the real API
uv run ruff check .      # lint
uv build                 # build sdist + wheel
```

## License

MIT

## Contributors


[![contributors](https://img.shields.io/github/contributors/Altech001/Nimo)](https://github.com/Altech001/Nimo)

