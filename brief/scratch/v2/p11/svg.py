"""Small helpers that draw the Part 11 diagrams with the page's CSS classes only."""

COLORED = {"bxo", "bxt", "bxg", "bxp"}


def svg(h, label, parts):
    assert 140 <= h <= 380
    return (f'<svg viewBox="0 0 560 {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="{label}">' + "".join(parts) + "</svg>")


def box(x, y, w, h, cls, label, check=True):
    need = 8 * len(label) + 24
    if check:
        assert w >= need, f"box {label!r} too narrow: {w} < {need}"
    assert x >= 8 and x + w <= 552, f"box {label!r} leaves the edge"
    tcls = "tk" if cls in COLORED else "t"
    cx, cy = x + w / 2, y + h / 2 + 5
    return (f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>'
            f'<text class="{tcls}" x="{cx:g}" y="{cy:g}" font-size="13" text-anchor="middle">{label}</text>')


def bar(x, y, w, h, cls, label):
    """A coloured bar (a span in a waterfall) with a label inside."""
    assert x >= 8 and x + w <= 552
    tcls = "tk" if cls in COLORED else "t"
    return (f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>'
            f'<text class="{tcls}" x="{x + w / 2:g}" y="{y + h / 2 + 5:g}" font-size="13" text-anchor="middle">{label}</text>')


def arrow(x1, y1, x2, y2, dashed=False, head=True):
    cls = "lnd" if dashed else "ln"
    end = ' marker-end="url(#ar)"' if head else ""
    return f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{end}/>'


def label(x, y, text, anchor="middle", main=False):
    cls, size = ("t", 13) if main else ("ts", 11)
    return f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{text}</text>'


def d47():
    p = [
        # top row: the app, the Docker engine, Fluent Bit
        box(16, 24, 128, 44, "bxt", "hello-devops"),
        arrow(146, 46, 196, 46), label(171, 38, "stdout"),
        box(200, 24, 136, 44, "bx", "Docker engine"),
        arrow(338, 46, 396, 46), label(367, 38, "forward"),
        box(400, 24, 136, 44, "bxo", "Fluent Bit"),
        label(468, 86, "parse to JSON"),
        # down to Elasticsearch
        arrow(468, 92, 468, 142), label(476, 122, "bulk API", anchor="start"),
        box(400, 146, 136, 44, "bxp", "Elasticsearch"),
        label(468, 208, "hello-logs-*"),
        # bottom row: you search through Kibana
        box(16, 146, 128, 44, "bx", "Your browser"),
        arrow(146, 168, 196, 168), label(171, 160, "5601"),
        box(200, 146, 136, 44, "bxg", "Kibana"),
        arrow(338, 168, 396, 168), label(367, 160, "search"),
        label(80, 86, "one line per event"),
        label(268, 86, "fluentd driver"),
    ]
    return svg(224, "A log line goes from hello-devops through the Docker engine to Fluent Bit, "
               "then to Elasticsearch, and you search it with Kibana", p)


def d48():
    p = [
        box(200, 12, 136, 40, "bxp", "Kubernetes API"),
        arrow(320, 54, 320, 92, dashed=True), label(312, 78, "labels", anchor="end"),
        # node 1
        label(16, 88, "node 1", anchor="start"),
        box(16, 96, 96, 44, "bxt", "app pod"),
        arrow(114, 118, 132, 118),
        box(136, 96, 112, 44, "bx", "log files"),
        arrow(250, 118, 268, 118),
        box(272, 96, 112, 44, "bxo", "Fluent Bit"),
        # node 2
        label(16, 188, "node 2", anchor="start"),
        box(16, 196, 96, 44, "bxt", "app pod"),
        arrow(114, 218, 132, 218),
        box(136, 196, 112, 44, "bx", "log files"),
        arrow(250, 218, 268, 218),
        box(272, 196, 112, 44, "bxo", "Fluent Bit"),
        # both ship to Elasticsearch outside the cluster
        arrow(386, 118, 412, 156),
        arrow(386, 218, 412, 182),
        box(416, 146, 136, 44, "bxg", "Elasticsearch"),
        label(484, 208, "k8s-logs-*"),
        label(192, 160, "/var/log/containers"),
        label(192, 260, "/var/log/containers"),
    ]
    return svg(276, "A Fluent Bit pod on every node tails the container log files, asks the Kubernetes API "
               "for pod labels, and sends records to Elasticsearch", p)


def d49():
    # The real slow trace from the lab: GET / took 835 ms, INCRBY took 832 ms of it.
    x0, scale = 128, 400 / 835
    p = [
        label(16, 22, "one trace: 0d99b605...", anchor="start"),
        label(16, 62, "GET /", anchor="start", main=True),
        label(16, 78, "server span", anchor="start"),
        bar(x0, 42, 400, 34, "bxo", "835 ms"),
        arrow(x0 + 6, 78, x0 + 6, 100, dashed=True, head=False),
        label(16, 122, "INCRBY", anchor="start", main=True),
        label(16, 138, "client span", anchor="start"),
        bar(x0 + 2, 102, round(832 * scale), 34, "bxt", "832 ms"),
        arrow(x0, 170, x0 + 400, 170, head=False),
        label(x0, 188, "0 ms"),
        label(round(x0 + 400 * scale), 188, "400 ms"),
        label(round(x0 + 800 * scale), 188, "800 ms"),
        arrow(x0, 164, x0, 176, head=False),
        arrow(round(x0 + 400 * scale), 164, round(x0 + 400 * scale), 176, head=False),
        arrow(round(x0 + 800 * scale), 164, round(x0 + 800 * scale), 176, head=False),
    ]
    return svg(204, "A trace waterfall: the GET / server span lasts 835 ms and its child INCRBY "
               "Redis span lasts 832 ms of that time", p)
