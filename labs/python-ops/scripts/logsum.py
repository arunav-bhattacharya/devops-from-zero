#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""logsum.py: summarize the Part 1 sample logs (labs/linux, copied to ~/code/linux-lab).

Examples:
  uv run scripts/logsum.py access ~/code/linux-lab/access.log
  uv run scripts/logsum.py access ~/code/linux-lab/access.log --max-error-rate 5
  uv run scripts/logsum.py app ~/code/linux-lab/app.log --format json

Exit codes: 0 all good, 1 over a limit you set, 2 bad usage or unreadable file.
"""

import argparse
import csv
import json
import logging
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

log = logging.getLogger("logsum")

# One line of the nginx "combined" format, for example:
# 203.0.113.7 - - [30/Oct/2026:09:00:08 +0000] "GET /api/cart HTTP/1.1" 200 4642 "-" "curl/8.5.0"
ACCESS_LINE = re.compile(
    r"(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "
    r'"(?P<method>[A-Z]+) (?P<path>\S+) [^"]*" '
    r"(?P<status>\d{3}) (?P<size>\d+|-)"
)

# One line of app.log, for example:
# 2026-10-30T09:04:30Z ERROR checkout-api req=8e9f0a database connection refused: orders-db:5432
APP_LINE = re.compile(
    r"(?P<time>\S+) (?P<level>[A-Z]+)\s+(?P<service>\S+) req=(?P<req>\S+) (?P<msg>.*)"
)


@dataclass
class AccessStats:
    requests: int = 0
    skipped: int = 0
    first: datetime | None = None
    last: datetime | None = None
    paths: Counter = field(default_factory=Counter)
    classes: Counter = field(default_factory=Counter)
    server_errors: Counter = field(default_factory=Counter)

    @property
    def error_rate(self) -> float:
        """Server errors (5xx) as a percentage of all requests."""
        if self.requests == 0:
            return 0.0
        return 100 * self.classes["5xx"] / self.requests


def parse_access(lines) -> AccessStats:
    stats = AccessStats()
    for number, line in enumerate(lines, start=1):
        match = ACCESS_LINE.match(line)
        if not match:
            # A bad line should not stop a 3 a.m. report, but it must be visible.
            stats.skipped += 1
            log.warning("line %d does not look like an access log line, skipped", number)
            continue
        stats.requests += 1
        # %z reads the "+0000" part, so `when` knows its time zone.
        when = datetime.strptime(match["time"], "%d/%b/%Y:%H:%M:%S %z")
        stats.first = when if stats.first is None else min(stats.first, when)
        stats.last = when if stats.last is None else max(stats.last, when)
        path = match["path"].split("?", 1)[0]  # /api/products?page=3 counts as /api/products
        status = int(match["status"])
        stats.paths[path] += 1
        stats.classes[f"{status // 100}xx"] += 1
        if status >= 500:
            stats.server_errors[f"{status} {path}"] += 1
    return stats


def parse_app(lines) -> dict:
    levels: Counter = Counter()
    errors: Counter = Counter()
    times = []
    continued = 0
    for number, line in enumerate(lines, start=1):
        if line[:1].isspace():
            continued += 1  # a stack trace line that belongs to the line above
            continue
        match = APP_LINE.match(line)
        if not match:
            log.warning("line %d does not look like an app log line, skipped", number)
            continue
        levels[match["level"]] += 1
        times.append(datetime.fromisoformat(match["time"]))  # "Z" works since Python 3.11
        if match["level"] == "ERROR":
            errors[match["msg"]] += 1
    return {"levels": levels, "errors": errors, "times": times, "continued": continued}


def read_lines(path: Path) -> list[str]:
    # errors="replace": one broken byte must not crash the whole report.
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def show_time(when: datetime | None, zone: ZoneInfo) -> str:
    return when.astimezone(zone).strftime("%Y-%m-%d %H:%M:%S %Z") if when else "-"


def write_csv(path: Path, stats: AccessStats) -> None:
    errors_by_path: Counter = Counter()
    for key, count in stats.server_errors.items():
        errors_by_path[key.split(" ", 1)[1]] += count
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["path", "requests", "server_errors"])
        for p, count in stats.paths.most_common():
            writer.writerow([p, count, errors_by_path[p]])
    log.info("wrote %d rows to %s", len(stats.paths), path)


def run_access(args) -> int:
    stats = parse_access(read_lines(args.file))
    ok = stats.error_rate <= args.max_error_rate
    if args.csv:
        write_csv(args.csv, stats)
    if args.format == "json":
        report = {
            "file": args.file.name,
            "requests": stats.requests,
            "skipped": stats.skipped,
            "first": stats.first.isoformat() if stats.first else None,
            "last": stats.last.isoformat() if stats.last else None,
            "status_classes": dict(sorted(stats.classes.items())),
            "error_rate": round(stats.error_rate, 2),
            "max_error_rate": args.max_error_rate,
            "ok": ok,
            "top_paths": stats.paths.most_common(args.top),
            "server_errors": stats.server_errors.most_common(),
        }
        print(json.dumps(report, indent=2))
    else:
        zone = args.tz
        print(f"{args.file.name}: {stats.requests} requests, {stats.skipped} skipped")
        print(f"from {show_time(stats.first, zone)} to {show_time(stats.last, zone)}")
        classes = ", ".join(f"{k} {v}" for k, v in sorted(stats.classes.items()))
        print(f"status: {classes}")
        print(f"error rate (5xx): {stats.error_rate:.1f}% (limit {args.max_error_rate:.1f}%)")
        print(f"\ntop {args.top} paths:")
        for p, count in stats.paths.most_common(args.top):
            print(f"{count:7}  {p}")
        print("\nserver errors:")
        for key, count in stats.server_errors.most_common():
            print(f"{count:7}  {key}")
    if not ok:
        log.error(
            "error rate %.1f%% is above the limit of %.1f%%", stats.error_rate, args.max_error_rate
        )
        return 1
    return 0


def run_app(args) -> int:
    result = parse_app(read_lines(args.file))
    levels, errors, times = result["levels"], result["errors"], result["times"]
    if args.format == "json":
        report = {
            "file": args.file.name,
            "levels": dict(levels),
            "first": min(times).isoformat() if times else None,
            "last": max(times).isoformat() if times else None,
            "stack_trace_lines": result["continued"],
            "top_errors": errors.most_common(args.top),
        }
        print(json.dumps(report, indent=2))
    else:
        zone = args.tz
        print(f"{args.file.name}: " + ", ".join(f"{k} {v}" for k, v in levels.most_common()))
        if times:
            print(f"from {show_time(min(times), zone)} to {show_time(max(times), zone)}")
        print(f"\ntop {args.top} errors:")
        for msg, count in errors.most_common(args.top):
            print(f"{count:7}  {msg}")
    if args.max_errors is not None and levels["ERROR"] > args.max_errors:
        log.error("%d ERROR lines, the limit is %d", levels["ERROR"], args.max_errors)
        return 1
    return 0


def zone(name: str) -> ZoneInfo:
    """argparse type: turn 'Europe/Berlin' into a time zone, or fail with a clear message."""
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        raise argparse.ArgumentTypeError(f"unknown time zone {name!r}") from None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="logsum", description="Summarize the Part 1 sample logs.")
    parser.add_argument("-v", "--verbose", action="store_true", help="also print debug messages")
    # Settings shared by both subcommands.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("file", type=Path, help="the log file to read")
    common.add_argument("--top", type=int, default=5, metavar="N", help="rows to show (default 5)")
    common.add_argument(
        "--format", choices=["text", "json"], default="text", help="text for people, json for jq"
    )
    common.add_argument(
        "--tz",
        type=zone,
        default="UTC",
        metavar="ZONE",
        help="show times in this zone (default UTC)",
    )

    sub = parser.add_subparsers(dest="command", required=True)
    access = sub.add_parser("access", parents=[common], help="nginx access log")
    access.add_argument(
        "--max-error-rate",
        type=float,
        metavar="PCT",
        # A flag beats the environment variable, which beats the default.
        default=float(os.environ.get("LOGSUM_MAX_ERROR_RATE", "1.0")),
        help="fail when more than this percent of requests are 5xx (default 1.0)",
    )
    access.add_argument(
        "--csv", type=Path, metavar="FILE", help="also write per-path counts to this CSV file"
    )
    access.set_defaults(handler=run_access)

    app = sub.add_parser("app", parents=[common], help="app log with levels")
    app.add_argument(
        "--max-errors", type=int, metavar="N", help="fail when there are more ERROR lines than N"
    )
    app.set_defaults(handler=run_app)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Log messages go to stderr, so stdout stays clean for the report (and for jq).
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="logsum: %(levelname)s %(message)s",
        stream=sys.stderr,
        force=True,
    )
    try:
        return args.handler(args)
    except FileNotFoundError:
        log.error("no such file: %s", args.file)
        return 2
    except PermissionError:
        log.error("no permission to read %s", args.file)
        return 2


if __name__ == "__main__":
    sys.exit(main())
