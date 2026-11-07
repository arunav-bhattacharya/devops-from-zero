"""Tests for scripts/healthcheck.py, against a tiny web server on 127.0.0.1."""

import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

import healthcheck


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/slow":
            time.sleep(1)
        status = 503 if self.path == "/down" else 200
        try:
            self.send_response(status)
            self.end_headers()
            self.wfile.write(b"ok")
        except (BrokenPipeError, ConnectionResetError):
            pass  # the client gave up (the timeout test does this on purpose)

    def log_message(self, *args):
        pass  # keep the test output quiet


@pytest.fixture
def server():
    """Start a web server on a free port and give back its base URL."""
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


def write_urls(tmp_path, *urls):
    path = tmp_path / "urls.txt"
    path.write_text("# a comment\n\n" + "\n".join(urls) + "\n", encoding="utf-8")
    return path


def test_all_up_exits_0(server, tmp_path, capsys):
    urls = write_urls(tmp_path, f"{server}/healthz", f"{server}/readyz")
    assert healthcheck.main([str(urls)]) == 0
    assert capsys.readouterr().out.count("OK") == 2


def test_one_down_exits_1(server, tmp_path, capsys):
    urls = write_urls(tmp_path, f"{server}/healthz", f"{server}/down")
    assert healthcheck.main([str(urls)]) == 1
    out, err = capsys.readouterr()
    assert "FAIL" in out and "HTTP 503" in out
    assert "1 of 2 URLs failed" in err


def test_slow_server_hits_the_timeout(server, tmp_path, capsys):
    urls = write_urls(tmp_path, f"{server}/slow")
    assert healthcheck.main([str(urls), "--timeout", "0.2"]) == 1
    assert "no answer after 0.2 s" in capsys.readouterr().out


def test_nothing_listening_exits_1(tmp_path, capsys):
    # Port 9 is "discard"; nothing listens there on a normal laptop or CI runner.
    urls = write_urls(tmp_path, "http://127.0.0.1:9/")
    assert healthcheck.main([str(urls), "--timeout", "1"]) == 1
    assert "cannot connect" in capsys.readouterr().out


def test_file_url_is_refused(tmp_path, capsys):
    urls = write_urls(tmp_path, "file:///etc/passwd")
    assert healthcheck.main([str(urls)]) == 2
    assert "not an http(s) URL" in capsys.readouterr().err
