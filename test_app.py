from app import app


def test_index_says_hello():
    client = app.test_client()
    body = client.get("/").get_json()
    assert body["message"] == "Hello, DevOps!"
    assert body["visits"] >= 1


def test_health_and_ready():
    client = app.test_client()
    assert client.get("/healthz").status_code == 200
    assert client.get("/readyz").status_code == 200


def test_metrics_are_exposed():
    client = app.test_client()
    client.get("/")
    assert b"hello_requests_total" in client.get("/metrics").data
