#!/usr/bin/env python3
"""Calculate 5xx / total request percentage from the Prometheus metrics endpoint."""

import argparse
import re
import sys
from urllib.request import urlopen

TOTAL = re.compile(r"^taskflow_requests_total\\s+(\\d+(?:\\.\\d+)?)$")
FAILED = re.compile(r"^taskflow_failed_requests_total\\s+(\\d+(?:\\.\\d+)?)$")


def metric_value(metrics: str, pattern: re.Pattern[str]) -> float:
    for line in metrics.splitlines():
        match = pattern.match(line)
        if match:
            return float(match.group(1))
    raise ValueError(f"Metric {pattern.pattern} not found")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--threshold", type=float, required=True)
    args = parser.parse_args()
    endpoint = f"{args.base_url.rstrip('/')}/metrics"
    try:
        with urlopen(endpoint, timeout=10) as response:
            metrics = response.read().decode("utf-8")
        total = metric_value(metrics, TOTAL)
        failed = metric_value(metrics, FAILED)
    except (OSError, UnicodeDecodeError, ValueError) as error:
        print(f"Could not calculate error rate: {error}", file=sys.stderr)
        return 2
    rate = (failed / total * 100) if total else 0.0
    print(
        f"total_requests={total:.0f} failed_5xx={failed:.0f} "
        f"error_rate={rate:.2f}% threshold={args.threshold:.2f}%"
    )
    if rate > args.threshold:
        print("Error-rate threshold exceeded", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
