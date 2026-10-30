"""A tiny stand-in for Slack or PagerDuty: print every alert Alertmanager sends.

Alertmanager POSTs JSON to http://webhook:5001/<receiver>. Watch the output with:
    docker compose logs -f webhook
It uses only the Python standard library, so there is nothing to install.
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class AlertHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        size = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(size))
        # One POST can carry several alerts: Alertmanager groups them.
        for alert in payload["alerts"]:
            labels = alert["labels"]
            print(
                f"[{payload['receiver']}] {alert['status'].upper()} "
                f"{labels['alertname']} job={labels.get('job', '-')} "
                f"severity={labels.get('severity', '-')}: "
                f"{alert['annotations'].get('summary', '')}",
                flush=True,
            )
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass  # skip the default access-log line for every POST


print("webhook: waiting for alerts on port 5001", flush=True)
HTTPServer(("0.0.0.0", 5001), AlertHandler).serve_forever()
