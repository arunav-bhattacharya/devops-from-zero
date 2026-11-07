#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""healthcheck.py: check a list of URLs and fail if any of them is down.

The file has one URL per line. Blank lines and lines that start with # are skipped.

Examples:
  uv run scripts/healthcheck.py scripts/urls.txt
  HEALTHCHECK_TIMEOUT=2 uv run scripts/healthcheck.py scripts/urls.txt

Exit codes: 0 every URL answered 2xx or 3xx, 1 at least one failed, 2 bad usage.
Only the standard library is used, so the script runs anywhere Python 3.12+ runs.
"""

import argparse
import logging
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

log = logging.getLogger("healthcheck")


def read_urls(path: Path) -> list[str]:
    urls = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if urlparse(line).scheme not in ("http", "https"):
            # urlopen also opens file:// and ftp:// URLs, which a health check never wants.
            raise ValueError(f"not an http(s) URL: {line}")
        urls.append(line)
    return urls


def check(url: str, timeout: float) -> tuple[bool, str]:
    """Ask for one URL. Return (ok, a short reason)."""
    request = urllib.request.Request(url, headers={"User-Agent": "python-ops-healthcheck"})
    start = time.monotonic()
    try:
        # read_urls() already refused anything that is not http or https.
        with urllib.request.urlopen(request, timeout=timeout) as response:
            ms = (time.monotonic() - start) * 1000
            return True, f"{response.status} in {ms:.0f} ms"
    except urllib.error.HTTPError as err:
        # urlopen raises for 4xx and 5xx answers: the server is up, but unhappy.
        return False, f"HTTP {err.code}"
    except urllib.error.URLError as err:
        # No answer at all: DNS failure, connection refused, TLS problem, timeout.
        if isinstance(err.reason, TimeoutError):
            return False, f"no answer after {timeout:g} s"
        return False, f"cannot connect ({err.reason})"
    except TimeoutError:
        # A timeout while reading the answer, after the connection was made.
        return False, f"no answer after {timeout:g} s"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="healthcheck", description="Check a list of URLs.")
    parser.add_argument("file", type=Path, help="a file with one URL per line")
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.environ.get("HEALTHCHECK_TIMEOUT", "5")),
        help="seconds to wait for each URL (default 5, or HEALTHCHECK_TIMEOUT)",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(format="healthcheck: %(message)s", stream=sys.stderr, force=True)

    try:
        urls = read_urls(args.file)
    except FileNotFoundError:
        log.error("no such file: %s", args.file)
        return 2
    except ValueError as err:
        log.error("%s", err)
        return 2
    if not urls:
        log.error("%s has no URLs in it", args.file)
        return 2

    failed = 0
    for url in urls:
        ok, reason = check(url, args.timeout)
        print(f"{'OK  ' if ok else 'FAIL'}  {url}  {reason}")
        failed += not ok
    if failed:
        log.error("%d of %d URLs failed", failed, len(urls))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
