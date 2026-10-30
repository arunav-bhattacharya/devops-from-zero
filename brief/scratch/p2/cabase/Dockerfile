# Sandbox-only helper: python:3.14-slim plus the sandbox proxy CA, so pip works here.
FROM python:3.14-slim
COPY ca-bundle.crt /etc/p2-ca.crt
ENV PIP_CERT=/etc/p2-ca.crt
