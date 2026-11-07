"""hello-devops: the tiny web app you ship all through the course."""

import os
import socket

import redis
from flask import Flask, jsonify
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

# Settings come from environment variables, so the same image runs anywhere.
APP_VERSION = os.getenv("APP_VERSION", "dev")
GREETING = os.getenv("GREETING", "Hello, DevOps!")
REDIS_HOST = os.getenv("REDIS_HOST", "")  # empty: count visits in memory

app = Flask(__name__)
REQUESTS = Counter("hello_requests_total", "Requests served", ["path"])
_visits = 0


def redis_client():
    return redis.Redis(host=REDIS_HOST, port=6379, socket_timeout=1)


def count_visit():
    global _visits
    if REDIS_HOST:
        return redis_client().incr("visits")
    _visits += 1
    return _visits


@app.get("/")
def index():
    REQUESTS.labels(path="/").inc()
    return jsonify(
        message=GREETING,
        version=APP_VERSION,
        host=socket.gethostname(),  # which container or pod answered
        visits=count_visit(),
    )


@app.get("/healthz")
def healthz():
    # Liveness: the process is up and can answer.
    return jsonify(status="ok")


@app.get("/readyz")
def readyz():
    # Readiness: the app can do real work (Redis answers, if we use it).
    if REDIS_HOST:
        try:
            redis_client().ping()
        except redis.RedisError:
            return jsonify(status="redis unavailable"), 503
    return jsonify(status="ready")


@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
