"""gh-runs: list recent GitHub Actions runs for a repository and fail if any failed.

Examples:
  export GITHUB_TOKEN="$(gh auth token)"
  uv run gh-runs arunav-bhattacharya/devops-from-zero
  uv run gh-runs YOUR-USER/hello-devops --branch main --limit 50

Exit codes: 0 no failed runs, 1 at least one failed run, 2 could not ask GitHub.
"""

import argparse
import logging
import os
import sys
from datetime import UTC, datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

log = logging.getLogger("gh-runs")

API = "https://api.github.com"
API_VERSION = "2026-03-10"  # pin the API version so a new one cannot change answers under you
TIMEOUT = (3.05, 10)  # seconds to connect, seconds to wait for each part of the answer
FAILED = {"failure", "timed_out", "startup_failure"}


def make_session(token: str | None, retries: int = 3, backoff: float = 1.0) -> requests.Session:
    """A session sends the same headers every time and reuses connections."""
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "python-ops-gh-runs",
        }
    )
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    # Retry GETs on 429 and 5xx, waiting longer each time (and as long as
    # Retry-After asks). Never retry 401 or 404: asking again cannot fix those.
    retry = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,  # hand back the last answer, so we can explain it
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def list_runs(
    session: requests.Session,
    repo: str,
    limit: int,
    branch: str | None = None,
    per_page: int = 100,
) -> list[dict]:
    """Return up to `limit` runs, newest first, following GitHub's pages."""
    url = f"{API}/repos/{repo}/actions/runs"
    params: dict | None = {"per_page": min(limit, per_page)}
    if branch:
        params["branch"] = branch
    runs: list[dict] = []
    while url and len(runs) < limit:
        response = session.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        runs.extend(response.json()["workflow_runs"])
        # The Link header holds the URL of the next page, query string included.
        url = response.links.get("next", {}).get("url")
        params = None
    return runs[:limit]


def explain(err: requests.HTTPError) -> str:
    """Turn an HTTP error into a sentence a person can act on."""
    response = err.response
    status = response.status_code
    if status == 401:
        return "GitHub says 401: the token is wrong or expired. Try: gh auth status"
    if status in (403, 429) and response.headers.get("x-ratelimit-remaining") == "0":
        reset = int(response.headers.get("x-ratelimit-reset", "0"))
        when = datetime.fromtimestamp(reset, tz=UTC).strftime("%H:%M UTC")
        return f"rate limit used up; it resets at {when}. A token raises the limit."
    if status == 404:
        return "GitHub says 404: no such repo, or your token cannot see it."
    return f"GitHub answered {status}: {response.text[:200]}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gh-runs", description=__doc__.splitlines()[0])
    parser.add_argument("repo", help="OWNER/NAME, for example octocat/hello-world")
    parser.add_argument("--branch", help="only runs for this branch")
    parser.add_argument("--limit", type=int, default=20, help="how many runs (default 20)")
    parser.add_argument(
        "--per-page", type=int, default=100, help="runs per request (default and maximum 100)"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="log every HTTP request")
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(name)s: %(message)s",
        stream=sys.stderr,
        force=True,
    )

    if args.repo.count("/") != 1:
        parser.error("repo must look like OWNER/NAME")  # prints usage and exits with 2
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        log.warning("GITHUB_TOKEN is not set: public repos only, 60 requests an hour")

    try:
        session = make_session(token)
        runs = list_runs(session, args.repo, args.limit, args.branch, args.per_page)
    except requests.HTTPError as err:
        log.error("%s", explain(err))
        return 2
    except requests.RequestException as err:
        # DNS failure, refused connection, timeout, too many retries
        log.error("could not reach GitHub: %s", err)
        return 2

    failed = [run for run in runs if run["conclusion"] in FAILED]
    for run in runs:
        result = run["conclusion"] or run["status"]  # conclusion is null while a run is going
        created = run["created_at"].replace("T", " ").removesuffix("Z")
        branch = run["head_branch"]
        print(f"#{run['run_number']:<5} {result:<10} {branch:<20} {created}  {run['name']}")
    print(f"{len(runs)} runs, {len(failed)} failed")
    for run in failed:
        log.error("failed: %s #%s %s", run["name"], run["run_number"], run["html_url"])
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
