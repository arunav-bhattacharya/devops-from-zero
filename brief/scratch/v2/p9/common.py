"""Shared links and helpers for Part 9 (Monitoring with Prometheus).

Every URL here came from the research notes (prometheus_grafana.md), from a
WebSearch result in this task, or was checked on raw.githubusercontent.com.
"""

import pathlib

ROOT = pathlib.Path("/home/user/devops-from-zero")
LAB = ROOT / "labs/hello-devops"
OBS = LAB / "observability"


def lab(rel):
    """Read a lab file so the lesson always shows exactly what was tested."""
    return (LAB / rel).read_text().rstrip("\n")


def ref(key, title=None, kind=None):
    t, u, k = L[key]
    return {"title": title or t, "url": u, "kind": kind or k}


def src(key):
    t, u, _ = L[key]
    return {"title": t, "url": u}


# key: (title, url, kind)
L = {
    # Google SRE books
    "sre_monitoring": ("Google SRE book: Monitoring distributed systems", "https://sre.google/sre-book/monitoring-distributed-systems/", "read"),
    "sre_slo": ("Google SRE book: Service level objectives", "https://sre.google/sre-book/service-level-objectives/", "read"),
    "sre_risk": ("Google SRE book: Embracing risk", "https://sre.google/sre-book/embracing-risk/", "read"),
    "sre_postmortem": ("Google SRE book: Postmortem culture", "https://sre.google/sre-book/postmortem-culture/", "read"),
    "sre_wb_alerting": ("Google SRE Workbook: Alerting on SLOs", "https://sre.google/workbook/alerting-on-slos/", "read"),
    "sre_wb_oncall": ("Google SRE Workbook: On-call", "https://sre.google/workbook/on-call/", "read"),
    # Methods
    "red_blog": ("The RED method (Tom Wilkie, Grafana Labs blog)", "https://grafana.com/blog/the-red-method-how-to-instrument-your-services/", "read"),
    "use": ("The USE method (Brendan Gregg)", "https://www.brendangregg.com/usemethod.html", "read"),
    "grafana_bp": ("Grafana: dashboard best practices (golden signals, RED, USE)", "https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/", "docs"),
    "medium_slo": ("How to alert on SLOs (Google Cloud on Medium)", "https://medium.com/google-cloud/how-to-alert-on-slos-2a5ce8c4e7dd", "read"),
    "otel_primer": ("OpenTelemetry: observability primer", "https://opentelemetry.io/docs/concepts/observability-primer/", "docs"),
    "otel_signals": ("OpenTelemetry: signals", "https://opentelemetry.io/docs/concepts/signals/", "docs"),
    # Videos (URLs from WebSearch results on youtube.com)
    "v_slo_ohmy": ("SLIs, SLOs, SLAs, oh my! (Google Cloud, Liz Fong-Jones and Seth Vargo)", "https://www.youtube.com/watch?v=tEylFyxbDLE", "watch"),
    "v_burn": ("Alerting on error budget burn rate (Google Cloud Tech)", "https://www.youtube.com/watch?v=t1BGo-Il1AM", "watch"),
    "v_red": ("The RED method: how to instrument your services (Tom Wilkie, KubeCon talk)", "https://www.youtube.com/watch?v=TJLpYXbnfQ4", "watch"),
    "v_how_prom": ("How Prometheus monitoring works (TechWorld with Nana)", "https://www.youtube.com/watch?v=h4Sl21AKiDg", "watch"),
    "v_intro_prom": ("Introduction to the Prometheus monitoring system (Julius Volz, Prometheus co-founder)", "https://www.youtube.com/watch?v=STVMGrYIlfg", "watch"),
    "v_promql": ("Intro to PromQL (Julius Volz)", "https://www.youtube.com/watch?v=MPN0SLE5YWk", "watch"),
    "v_hist": ("Understanding Prometheus histograms (PromLabs, Julius Volz)", "https://www.youtube.com/watch?v=yYbXak-1hew", "watch"),
    "v_guesswork": ("Taking the guesswork out of your PromQL (Julius Volz, KubeCon talk)", "https://www.youtube.com/watch?v=3hKdcFwMozI", "watch"),
    "v_k8s_operator": ("Prometheus monitoring on Kubernetes with Helm and the Prometheus Operator (TechWorld with Nana)", "https://www.youtube.com/watch?v=QoDqxm7ybLc", "watch"),
    "v_pitfalls": ("PromCon 2017: Best practices and beastly pitfalls (Julius Volz)", "https://www.youtube.com/watch?v=_MNYuTNfTb4", "watch"),
    "v_promlabs": ("PromLabs YouTube channel (Prometheus monitoring with Julius)", "https://www.youtube.com/@PromLabs", "watch"),
    # Prometheus docs
    "overview": ("Prometheus: overview and architecture", "https://prometheus.io/docs/introduction/overview/", "docs"),
    "data_model": ("Prometheus: data model", "https://prometheus.io/docs/concepts/data_model/", "docs"),
    "metric_types": ("Prometheus: metric types", "https://prometheus.io/docs/concepts/metric_types/", "docs"),
    "understanding_types": ("Prometheus tutorial: understanding metric types", "https://prometheus.io/docs/tutorials/understanding_metric_types/", "docs"),
    "storage": ("Prometheus: storage and retention", "https://prometheus.io/docs/prometheus/latest/storage/", "docs"),
    "exposition": ("Prometheus: exposition formats", "https://prometheus.io/docs/instrumenting/exposition_formats/", "docs"),
    "instrumentation": ("Prometheus: instrumentation best practices", "https://prometheus.io/docs/practices/instrumentation/", "docs"),
    "naming": ("Prometheus: metric and label naming", "https://github.com/prometheus/docs/blob/main/docs/practices/naming.md", "docs"),
    "pushing": ("Prometheus: when to use the Pushgateway", "https://github.com/prometheus/docs/blob/main/docs/practices/pushing.md", "docs"),
    "prom3_blog": ("Announcing Prometheus 3.0 (Prometheus blog)", "https://prometheus.io/blog/2024/11/14/prometheus-3-0/", "read"),
    "cardinality": ("Cardinality is key (Robust Perception)", "https://www.robustperception.io/cardinality-is-key/", "read"),
    "node_exporter": ("node_exporter README", "https://github.com/prometheus/node_exporter", "docs"),
    "blackbox": ("blackbox_exporter README", "https://github.com/prometheus/blackbox_exporter", "docs"),
    "config": ("Prometheus: configuration reference", "https://github.com/prometheus/prometheus/blob/main/docs/configuration/configuration.md", "docs"),
    "basics": ("Prometheus: querying basics", "https://prometheus.io/docs/prometheus/latest/querying/basics/", "docs"),
    "functions": ("Prometheus: query functions", "https://prometheus.io/docs/prometheus/latest/querying/functions/", "docs"),
    "operators": ("Prometheus: operators and vector matching", "https://prometheus.io/docs/prometheus/latest/querying/operators/", "docs"),
    "examples": ("Prometheus: query examples", "https://prometheus.io/docs/prometheus/latest/querying/examples/", "docs"),
    "histograms": ("Prometheus: histograms and summaries", "https://prometheus.io/docs/practices/histograms/", "docs"),
    "rules_practice": ("Prometheus: recording rule naming", "https://prometheus.io/docs/practices/rules/", "docs"),
    "recording_rules": ("Prometheus: defining recording rules", "https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/", "docs"),
    "alerting_rules": ("Prometheus: alerting rules", "https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/", "docs"),
    "unit_tests": ("Prometheus: unit testing for rules", "https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/", "docs"),
    "prom_alerting_practice": ("Prometheus: alerting best practices", "https://prometheus.io/docs/practices/alerting/", "docs"),
    "am_overview": ("Alertmanager: overview", "https://prometheus.io/docs/alerting/latest/alertmanager/", "docs"),
    "am_config": ("Alertmanager: configuration", "https://prometheus.io/docs/alerting/latest/configuration/", "docs"),
    "alerting_tutorial": ("Prometheus tutorial: alerting based on metrics", "https://prometheus.io/docs/tutorials/alerting_based_on_metrics/", "docs"),
    "rp_rate_range": ("What range should I use with rate()? (Robust Perception)", "https://www.robustperception.io/what-range-should-i-use-with-rate/", "read"),
    "rp_rate_then_sum": ("Rate then sum, never sum then rate (Robust Perception)", "https://www.robustperception.io/rate-then-sum-never-sum-then-rate/", "read"),
    "rp_irate": ("Avoid irate() in alerts (Robust Perception)", "https://www.robustperception.io/avoid-irate-in-alerts/", "read"),
    "promlabs_rates": ("How exactly does PromQL calculate rates? (PromLabs)", "https://promlabs.com/blog/2021/01/29/how-exactly-does-promql-calculate-rates/", "read"),
    "rp_hist": ("How does a Prometheus histogram work? (Robust Perception)", "https://www.robustperception.io/how-does-a-prometheus-histogram-work/", "read"),
    # Kubernetes and scale
    "kps_chart": ("kube-prometheus-stack Helm chart", "https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack", "docs"),
    "operator": ("Prometheus Operator", "https://github.com/prometheus-operator/prometheus-operator", "docs"),
    "operator_gs": ("Prometheus Operator: getting started with ServiceMonitors", "https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/developer/getting-started.md", "docs"),
    "operator_trouble": ("Prometheus Operator: troubleshooting ServiceMonitors", "https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/platform/troubleshooting.md", "docs"),
    "ksm": ("kube-state-metrics README", "https://github.com/kubernetes/kube-state-metrics", "docs"),
    "metrics_server": ("metrics-server README", "https://github.com/kubernetes-sigs/metrics-server", "docs"),
    "thanos": ("Thanos", "https://github.com/thanos-io/thanos", "docs"),
    "mimir": ("Grafana Mimir", "https://github.com/grafana/mimir", "docs"),
    "remote_write": ("Prometheus: remote write tuning", "https://github.com/prometheus/docs/blob/main/docs/practices/remote_write.md", "docs"),
    # Python client
    "client_python": ("Prometheus Python client", "https://github.com/prometheus/client_python", "docs"),
    "client_flask": ("Python client: exposing metrics from Flask", "https://github.com/prometheus/client_python/blob/master/docs/content/exporting/http/flask.md", "docs"),
    "client_multiproc": ("Python client: multiprocess mode", "https://github.com/prometheus/client_python/blob/master/docs/content/multiprocess/_index.md", "docs"),
    "client_hist": ("Python client: histograms", "https://github.com/prometheus/client_python/blob/master/docs/content/instrumenting/histogram.md", "docs"),
}
