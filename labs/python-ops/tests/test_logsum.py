"""Tests for scripts/logsum.py. Run them with: uv run pytest"""

import json
from pathlib import Path

import pytest

import logsum

# The Part 1 sample log: next to this lab in the course repo, or where Day 3 copied it.
CANDIDATES = [
    Path(__file__).resolve().parents[2] / "linux" / "access.log",
    Path.home() / "code" / "linux-lab" / "access.log",
]
SAMPLE = next((p for p in CANDIDATES if p.exists()), CANDIDATES[0])

LINES = [
    '192.0.2.1 - - [30/Oct/2026:09:00:00 +0000] "GET /api/cart HTTP/1.1" 200 10 "-" "curl/8"',
    '192.0.2.1 - - [30/Oct/2026:09:01:00 +0000] "GET /api/cart?x=1 HTTP/1.1" 500 10 "-" "curl/8"',
    "this line is broken",
    '192.0.2.2 - - [30/Oct/2026:09:02:00 +0000] "POST /login HTTP/1.1" 302 0 "-" "curl/8"',
]


@pytest.fixture
def access_log(tmp_path: Path) -> Path:
    """A small access log in a fresh temporary folder, deleted by pytest later."""
    path = tmp_path / "access.log"
    path.write_text("\n".join(LINES) + "\n", encoding="utf-8")
    return path


def test_parse_counts_paths_without_query_strings():
    stats = logsum.parse_access(LINES)
    assert stats.requests == 3
    assert stats.skipped == 1
    assert stats.paths["/api/cart"] == 2
    assert stats.server_errors == {"500 /api/cart": 1}


def test_times_keep_their_time_zone():
    stats = logsum.parse_access(LINES)
    assert stats.first.utcoffset().total_seconds() == 0
    assert (stats.last - stats.first).total_seconds() == 120


def test_over_the_limit_exits_1_and_says_why(access_log, capsys):
    # One of three requests is a 5xx: 33% is above the default limit of 1%.
    code = logsum.main(["access", str(access_log)])
    out, err = capsys.readouterr()
    assert code == 1
    assert "error rate (5xx): 33.3%" in out
    assert "above the limit" in err  # the reason goes to stderr, not stdout
    assert "line 3 does not look like" in err


def test_flag_raises_the_limit(access_log):
    assert logsum.main(["access", str(access_log), "--max-error-rate", "50"]) == 0


def test_environment_variable_sets_the_default(access_log, monkeypatch):
    # monkeypatch undoes this change after the test, so other tests never see it.
    monkeypatch.setenv("LOGSUM_MAX_ERROR_RATE", "50")
    assert logsum.main(["access", str(access_log)]) == 0


def test_json_output_is_valid_json(access_log, capsys):
    logsum.main(["access", str(access_log), "--format", "json", "--max-error-rate", "50"])
    report = json.loads(capsys.readouterr().out)
    assert report["requests"] == 3
    assert report["ok"] is True
    assert report["top_paths"][0] == ["/api/cart", 2]


def test_csv_file_is_written(access_log, tmp_path):
    out = tmp_path / "paths.csv"
    logsum.main(["access", str(access_log), "--csv", str(out), "--max-error-rate", "50"])
    rows = out.read_text(encoding="utf-8").splitlines()
    assert rows[0] == "path,requests,server_errors"
    assert rows[1] == "/api/cart,2,1"


def test_missing_file_exits_2(tmp_path, capsys):
    assert logsum.main(["access", str(tmp_path / "nope.log")]) == 2
    assert "no such file" in capsys.readouterr().err


def test_bad_time_zone_is_a_usage_error():
    with pytest.raises(SystemExit) as exit_info:
        logsum.main(["access", "x.log", "--tz", "Mars/Olympus"])
    assert exit_info.value.code == 2  # argparse exits with 2 on bad arguments


def test_app_log_counts_levels_and_skips_stack_traces(tmp_path, capsys):
    path = tmp_path / "app.log"
    path.write_text(
        "2026-10-30T09:00:01Z INFO  api req=- started\n"
        "2026-10-30T09:00:02Z ERROR api req=a1 NullPointerException in Cart.total\n"
        "    at com.shop.Cart.total(Cart.kt:42)\n",
        encoding="utf-8",
    )
    assert logsum.main(["app", str(path), "--max-errors", "0"]) == 1
    out = capsys.readouterr().out
    assert "INFO 1, ERROR 1" in out
    assert "NullPointerException in Cart.total" in out


@pytest.mark.skipif(not SAMPLE.exists(), reason="the Part 1 sample access.log was not found")
def test_sample_log_matches_the_day_5_numbers():
    stats = logsum.parse_access(logsum.read_lines(SAMPLE))
    assert stats.requests == 238
    assert stats.server_errors.most_common(1) == [("500 /api/checkout", 6)]
    assert round(stats.error_rate, 1) == 4.6
