"""Add RED metrics (rate, errors, duration) to hello-devops without editing app.py.

app.py only counts visits to "/" in hello_requests_total. It does not record
status codes or how long a request took. This file imports the unchanged app
and adds two Flask hooks: one runs before every request, one after it.

compose.yaml starts gunicorn with "red_metrics:app" instead of "app:app".
Both metrics land in the same registry, so the app's /metrics page shows them.
"""

import time

from flask import g, request
from prometheus_client import Counter, Histogram

from app import app  # the hello-devops app, unchanged

# Every response, labelled by route and status code ("200", "404", "500").
RESPONSES = Counter(
    "hello_responses_total",
    "HTTP responses sent, by route and status code",
    ["path", "status"],
)

# How long each request took, in seconds, counted into buckets.
# No buckets given, so the client's defaults apply: 5 ms up to 10 s.
DURATION = Histogram(
    "hello_request_duration_seconds",
    "Time spent handling a request, in seconds",
    ["path"],
)


@app.before_request
def start_timer():
    g.start = time.perf_counter()


@app.after_request
def record(response):
    # Use the route pattern ("/", "/healthz"), never the raw URL.
    # Raw URLs would give one time series per URL anyone ever typed.
    path = request.url_rule.rule if request.url_rule else "unmatched"
    if path != "/metrics":  # do not count Prometheus's own scrapes
        RESPONSES.labels(path=path, status=str(response.status_code)).inc()
        DURATION.labels(path=path).observe(time.perf_counter() - g.start)
    return response
