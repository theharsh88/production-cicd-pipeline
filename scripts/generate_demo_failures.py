#!/usr/bin/env python3
"""Generate bounded, opt-in error traffic for a rollback demonstration."""

import argparse
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--requests", type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.requests <= 100:
        print("--requests must be between 1 and 100", file=sys.stderr)
        return 2
    url = f"{args.base_url.rstrip('/')}/api/demo/failure"
    failures = 0
    for _ in range(args.requests):
        try:
            with urlopen(url, timeout=5) as response:
                if response.status >= 500:
                    failures += 1
        except HTTPError as error:
            if error.code == 500:
                failures += 1
            else:
                print(f"Unexpected response: {error.code}", file=sys.stderr)
                return 1
        except URLError as error:
            print(f"Could not contact demo endpoint: {error.reason}", file=sys.stderr)
            return 1
    print(f"Generated {failures}/{args.requests} controlled 5xx responses")
    return 0 if failures == args.requests else 1


if __name__ == "__main__":
    raise SystemExit(main())
