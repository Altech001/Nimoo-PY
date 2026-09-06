import sys

from nimoo import InvalidPhoneNumberError, NetworkError, NimoAPIError, verify


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    try:
        result = verify(sys.argv[1])
    except InvalidPhoneNumberError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except (NimoAPIError, NetworkError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"msisdn:    {result.msisdn}")
    print(f"status:    {result.status}")
    print(f"full name: {result.full_name or '-'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
