#!/usr/bin/env python3
"""Write labs/hello-devops/observability/grafana/dashboards/hello-red.json.

The dashboard is classic Grafana JSON (the format file provisioning loads).
Layout for an operator: RED stats on top, RED graphs below, details in a
collapsed row at the bottom.
"""
import json
import pathlib
import sys

OUT = pathlib.Path("/home/user/devops-from-zero/labs/hello-devops/observability/grafana/dashboards/hello-red.json")
DS = {"type": "prometheus", "uid": "prometheus"}
SEL = 'job=~"$job", path=~"$path"'
SCHEMA = int(sys.argv[1]) if len(sys.argv) > 1 else 42

_id = 0


def nid():
    global _id
    _id += 1
    return _id


def target(expr, legend="__auto", ref="A", instant=False, fmt="time_series"):
    t = {"refId": ref, "datasource": DS, "expr": expr, "legendFormat": legend, "range": not instant, "instant": instant}
    if fmt != "time_series":
        t["format"] = fmt
    return t


def thresholds(*steps):
    out = [{"color": "green", "value": None}]
    for color, value in steps:
        out.append({"color": color, "value": value})
    return {"mode": "absolute", "steps": out}


def stat(title, desc, expr, unit, x, th, decimals=None, mappings=None):
    defaults = {"unit": unit, "thresholds": th, "color": {"mode": "thresholds"}}
    if decimals is not None:
        defaults["decimals"] = decimals
    if mappings:
        defaults["mappings"] = mappings
    return {
        "id": nid(), "type": "stat", "title": title, "description": desc, "datasource": DS,
        "gridPos": {"h": 4, "w": 6, "x": x, "y": 0},
        "fieldConfig": {"defaults": defaults, "overrides": []},
        "options": {"colorMode": "background", "graphMode": "area", "justifyMode": "auto",
                    "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
                    "textMode": "value"},
        "targets": [target(expr, legend=title)],
    }


def series(title, desc, targets, unit, x, y, w=8, h=8, th=None, overrides=None, show_th=False, stack=False):
    custom = {"drawStyle": "line", "lineWidth": 2, "fillOpacity": 10, "showPoints": "never",
              "spanNulls": False, "thresholdsStyle": {"mode": "line+area" if show_th else "off"}}
    if stack:
        custom["stacking"] = {"mode": "normal", "group": "A"}
    defaults = {"unit": unit, "custom": custom, "min": 0, "color": {"mode": "palette-classic"}}
    if th:
        defaults["thresholds"] = th
    return {
        "id": nid(), "type": "timeseries", "title": title, "description": desc, "datasource": DS,
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "fieldConfig": {"defaults": defaults, "overrides": overrides or []},
        "options": {"legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
                    "tooltip": {"mode": "multi", "sort": "desc"}},
        "targets": targets,
    }


# "or vector(0)": with no 5xx at all, the top half returns nothing, and the
# panel would say "No data" instead of 0%.
ERR_RATIO = (f'(sum(rate(hello_responses_total{{{SEL}, status=~"5.."}}[$__rate_interval])) or vector(0))\n/\n'
             f'sum(rate(hello_responses_total{{{SEL}}}[$__rate_interval]))')


def quant(q):
    return (f'histogram_quantile({q}, sum by (le) '
            f'(rate(hello_request_duration_seconds_bucket{{{SEL}}}[$__rate_interval])))')


panels = [
    # Row 1: four numbers that answer "is it OK right now?"
    stat("Requests per second", "Rate: all responses per second, summed over the selected paths.",
         f'sum(rate(hello_responses_total{{{SEL}}}[$__rate_interval]))', "reqps", 0,
         thresholds(), decimals=2),
    stat("Error ratio (5xx)", "Errors: the share of responses with a 5xx status. Green under 1%, orange from 1%, red from 5%.",
         ERR_RATIO, "percentunit", 6, thresholds(("orange", 0.01), ("red", 0.05)), decimals=1),
    stat("p95 latency", "Duration: 95% of requests finished faster than this. Orange from 250 ms, red from 1 s.",
         quant(0.95), "s", 12, thresholds(("orange", 0.25), ("red", 1)), decimals=3),
    stat("Scrape target", "Is Prometheus able to scrape the app? 1 means yes (UP), 0 means no (DOWN).",
         'min(up{job=~"$job"})', "none", 18,
         {"mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}]},
         mappings=[{"type": "value", "options": {"0": {"text": "DOWN", "color": "red", "index": 0},
                                                 "1": {"text": "UP", "color": "green", "index": 1}}}]),
    # Row 2: the same three signals over time
    series("Rate: requests per second by status", "Responses per second, one line per HTTP status code.",
           [target(f'sum by (status) (rate(hello_responses_total{{{SEL}}}[$__rate_interval]))', "{{status}}")],
           "reqps", 0, 4,
           overrides=[{"matcher": {"id": "byRegexp", "options": "5.."},
                       "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "red"}}]}]),
    series("Errors: share of requests failing", "The 5xx error ratio over time. The red area starts at 5%.",
           [target(ERR_RATIO, "5xx ratio")], "percentunit", 8, 4,
           th=thresholds(("red", 0.05)), show_th=True),
    series("Duration: p50, p95 and p99 latency", "How long requests take. Each line is a percentile from the histogram.",
           [target(quant(0.5), "p50", "A"), target(quant(0.95), "p95", "B"), target(quant(0.99), "p99", "C")],
           "s", 16, 4),
]

# Row 3: details for when the top says something is wrong (collapsed by default)
details = [
    {
        "id": nid(), "type": "table", "title": "Requests by path and status (last 5 minutes)",
        "description": "One row per path and status. Built from one instant query plus two transformations.",
        "datasource": DS, "gridPos": {"h": 8, "w": 12, "x": 0, "y": 13},
        "fieldConfig": {"defaults": {"unit": "short", "decimals": 0}, "overrides": []},
        "options": {"showHeader": True, "sortBy": [{"displayName": "Requests", "desc": True}]},
        "targets": [target(f'sum by (path, status) (increase(hello_responses_total{{{SEL}}}[5m]))',
                           instant=True, fmt="table")],
        "transformations": [
            {"id": "organize", "options": {"excludeByName": {"Time": True},
                                           "indexByName": {"path": 0, "status": 1, "Value": 2},
                                           "renameByName": {"path": "Path", "status": "Status", "Value": "Requests"}}},
            {"id": "sortBy", "options": {"sort": [{"field": "Requests", "desc": True}]}},
        ],
    },
    {
        "id": nid(), "type": "heatmap", "title": "Latency heatmap",
        "description": "How many requests fell into each latency bucket, over time. Darker means more requests.",
        "datasource": DS, "gridPos": {"h": 8, "w": 12, "x": 12, "y": 13},
        "fieldConfig": {"defaults": {}, "overrides": []},
        "options": {"calculate": False, "yAxis": {"unit": "s"}, "cellGap": 1,
                    "color": {"mode": "scheme", "scheme": "Oranges", "steps": 64},
                    "tooltip": {"mode": "single", "yHistogram": False}},
        "targets": [target(f'sum by (le) (rate(hello_request_duration_seconds_bucket{{{SEL}}}[$__rate_interval]))',
                           "{{le}}", fmt="heatmap")],
    },
]

panels.append({"id": nid(), "type": "row", "title": "Details", "collapsed": True,
               "gridPos": {"h": 1, "w": 24, "x": 0, "y": 12}, "panels": details})


def var(name, label, metric, match, multi):
    q = f"label_values({metric}{match},{name})"
    v = {"name": name, "label": label, "type": "query", "datasource": DS,
         "definition": q,
         "query": {"qryType": 1, "query": q, "refId": "PrometheusVariableQueryEditor-VariableQuery"},
         "refresh": 1, "sort": 1, "regex": "", "multi": multi, "includeAll": multi}
    if multi:
        v["allValue"] = ".*"
        v["current"] = {"text": "All", "value": "$__all"}
    return v


dash = {
    "uid": "hello-red",
    "title": "hello-devops: RED",
    "description": "Rate, errors and duration for hello-devops. Provisioned from grafana/dashboards/hello-red.json.",
    "tags": ["hello-devops", "red"],
    "timezone": "browser",
    "editable": True,
    "graphTooltip": 1,  # shared crosshair: hover one graph, see the same moment on all
    "refresh": "30s",
    "time": {"from": "now-30m", "to": "now"},
    "schemaVersion": SCHEMA,
    "templating": {"list": [
        var("job", "Job", "hello_responses_total", "", False),
        var("path", "Path", "hello_responses_total", '{job=~"$job"}', True),
    ]},
    "annotations": {"list": [
        {"builtIn": 1, "name": "Annotations & Alerts", "type": "dashboard", "enable": True, "hide": True,
         "iconColor": "rgba(0, 211, 255, 1)",
         "datasource": {"type": "grafana", "uid": "-- Grafana --"}},
        {"name": "Prometheus alerts", "enable": True, "iconColor": "red", "datasource": DS,
         "expr": 'ALERTS{alertstate="firing", job=~"$job"}', "step": "15s",
         "titleFormat": "{{alertname}}", "textFormat": "{{severity}}", "tagKeys": "severity"},
    ]},
    "panels": panels,
}

def dump(o, ind=0, width=110):
    """JSON with 2-space indent, but short lists and objects stay on one line."""
    one = json.dumps(o)
    if not isinstance(o, (dict, list)) or len(one) + ind <= width:
        return one
    pad, inner = " " * ind, " " * (ind + 2)
    if isinstance(o, list):
        items = [inner + dump(v, ind + 2, width) for v in o]
        return "[\n" + ",\n".join(items) + "\n" + pad + "]"
    items = [inner + json.dumps(k) + ": " + dump(v, ind + 2, width) for k, v in o.items()]
    return "{\n" + ",\n".join(items) + "\n" + pad + "}"


OUT.write_text(dump(dash) + "\n")
assert json.loads(OUT.read_text()) == dash
print(f"wrote {OUT} ({len(OUT.read_text().splitlines())} lines)")
