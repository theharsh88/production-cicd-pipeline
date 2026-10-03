"""Small dependency-free Prometheus-compatible request metrics registry."""

from collections import Counter
from threading import Lock
from time import monotonic


class Metrics:
    def __init__(self) -> None:
        self.started_at = monotonic()
        self.lock = Lock()
        self.requests = 0
        self.successes = 0
        self.failures = 0
        self.status_codes: Counter[int] = Counter()

    def record(self, status_code: int) -> None:
        with self.lock:
            self.requests += 1
            self.status_codes[status_code] += 1
            if status_code >= 500:
                self.failures += 1
            else:
                self.successes += 1

    def render(self, version: str) -> str:
        with self.lock:
            lines = [
                "# HELP taskflow_requests_total Total HTTP requests.",
                "# TYPE taskflow_requests_total counter",
                f"taskflow_requests_total {self.requests}",
                "# HELP taskflow_successful_requests_total Non-5xx HTTP responses.",
                "# TYPE taskflow_successful_requests_total counter",
                f"taskflow_successful_requests_total {self.successes}",
                "# HELP taskflow_failed_requests_total HTTP 5xx responses.",
                "# TYPE taskflow_failed_requests_total counter",
                f"taskflow_failed_requests_total {self.failures}",
                "# HELP taskflow_uptime_seconds Process uptime in seconds.",
                "# TYPE taskflow_uptime_seconds gauge",
                f"taskflow_uptime_seconds {monotonic() - self.started_at:.3f}",
                "# HELP taskflow_application_info Immutable application version.",
                "# TYPE taskflow_application_info gauge",
                f'taskflow_application_info{{version="{version}"}} 1',
            ]
            for code, count in sorted(self.status_codes.items()):
                lines.append(
                    f'taskflow_http_responses_total{{status="{code}"}} {count}'
                )
            return "\n".join(lines) + "\n"


metrics = Metrics()
