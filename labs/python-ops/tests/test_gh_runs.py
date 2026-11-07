"""Tests for gh-runs. The responses library answers in place of api.github.com."""

import pytest
import responses
from responses import matchers, registries

from python_ops import gh_runs

RUNS_URL = "https://api.github.com/repos/octo/shop/actions/runs"


def run(number, conclusion="success", status="completed"):
    return {
        "run_number": number,
        "name": "ci",
        "head_branch": "main",
        "status": status,
        "conclusion": conclusion,
        "created_at": "2026-11-07T09:00:00Z",
        "html_url": f"https://github.com/octo/shop/actions/runs/{number}",
    }


@pytest.fixture
def token(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")


@responses.activate
def test_sends_token_and_version_headers(token):
    responses.get(
        RUNS_URL,
        json={"workflow_runs": [run(3)]},
        match=[
            matchers.header_matcher(
                {"Authorization": "Bearer test-token", "X-GitHub-Api-Version": "2026-03-10"}
            ),
            matchers.query_param_matcher({"per_page": "20"}),
        ],
    )
    assert gh_runs.main(["octo/shop"]) == 0


@responses.activate
def test_follows_the_link_header_to_the_next_page(token):
    page2 = "https://api.github.com/repositories/42/actions/runs?per_page=2&page=2"
    responses.get(
        RUNS_URL,
        json={"workflow_runs": [run(5), run(4)]},
        headers={"Link": f'<{page2}>; rel="next"'},
    )
    responses.get(page2, json={"workflow_runs": [run(3), run(2)]})
    session = gh_runs.make_session("test-token")
    runs = gh_runs.list_runs(session, "octo/shop", limit=3, per_page=2)
    assert [r["run_number"] for r in runs] == [5, 4, 3]
    assert len(responses.calls) == 2


@responses.activate
def test_failed_run_exits_1_and_names_it(token, capsys):
    responses.get(RUNS_URL, json={"workflow_runs": [run(8), run(7, conclusion="failure")]})
    assert gh_runs.main(["octo/shop"]) == 1
    out, err = capsys.readouterr()
    assert "2 runs, 1 failed" in out
    assert "actions/runs/7" in err


@responses.activate
def test_run_in_progress_shows_its_status(token, capsys):
    responses.get(RUNS_URL, json={"workflow_runs": [run(9, conclusion=None, status="in_progress")]})
    assert gh_runs.main(["octo/shop"]) == 0
    assert "in_progress" in capsys.readouterr().out


@responses.activate(registry=registries.OrderedRegistry)
def test_retries_a_502_then_succeeds(token):
    # OrderedRegistry hands out the answers in this order, one per request.
    responses.get(RUNS_URL, status=502)
    responses.get(RUNS_URL, json={"workflow_runs": [run(1)]})
    session = gh_runs.make_session("test-token", backoff=0)  # no waiting in tests
    assert len(gh_runs.list_runs(session, "octo/shop", limit=5)) == 1
    assert len(responses.calls) == 2


@responses.activate
def test_bad_token_exits_2_with_a_hint(token, capsys):
    responses.get(RUNS_URL, status=401, json={"message": "Bad credentials"})
    assert gh_runs.main(["octo/shop"]) == 2
    assert "gh auth status" in capsys.readouterr().err
    assert len(responses.calls) == 1  # a 401 is never retried


@responses.activate
def test_rate_limit_says_when_it_resets(token, capsys):
    responses.get(
        RUNS_URL,
        status=403,
        headers={"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1793955600"},
    )
    assert gh_runs.main(["octo/shop"]) == 2
    assert "resets at 09:00 UTC" in capsys.readouterr().err


def test_no_token_warns(monkeypatch, capsys):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with responses.RequestsMock() as mock:
        mock.get(RUNS_URL, json={"workflow_runs": []})
        assert gh_runs.main(["octo/shop"]) == 0
    assert "GITHUB_TOKEN is not set" in capsys.readouterr().err
