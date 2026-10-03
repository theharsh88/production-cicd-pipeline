#!/usr/bin/env python3
"""Run a non-destructive deployment smoke test against a TaskFlow instance."""

import argparse
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request(
    url: str, method: str = "GET", body: bytes | None = None
) -> tuple[int, bytes]:
    try:
        with urlopen(Request(url, method=method, data=body), timeout=10) as response:
            return response.status, response.read()
    except HTTPError as error:
        return error.code, error.read()
    except URLError as error:
        raise RuntimeError(f"Could not contact {url}: {error.reason}") from error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    health_status, _ = request(f"{base_url}/health")
    list_status, _ = request(f"{base_url}/api/tasks")
    if health_status != 200 or list_status != 200:
        print(
            f"Smoke test failed: health={health_status}, tasks={list_status}",
            file=sys.stderr,
        )
        return 1
    print(f"Smoke test passed for {base_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
