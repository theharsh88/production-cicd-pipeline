#!/usr/bin/env python3
"""Poll /health until healthy or the deployment deadline is reached."""

import argparse
import json
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--interval", type=float, default=2)
    args = parser.parse_args()
    endpoint = f"{args.base_url.rstrip('/')}/health"
    deadline = time.monotonic() + args.timeout
    last_error = "service did not respond"
    while time.monotonic() < deadline:
        try:
            with urlopen(endpoint, timeout=5) as response:
                payload = json.load(response)
            if response.status == 200 and payload.get("status") == "healthy":
                print(f"Healthy: version={payload.get('version', 'unknown')}")
                return 0
            last_error = f"unexpected status or body: {payload}"
        except (URLError, json.JSONDecodeError) as error:
            last_error = str(error)
        time.sleep(args.interval)
    print(f"Health check timed out for {endpoint}: {last_error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
