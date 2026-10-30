# syntax=docker/dockerfile:1

# ---- build stage: install dependencies into a virtual environment ----
FROM python:3.14-slim AS build
WORKDIR /app
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- run stage: only what the app needs at run time ----
FROM python:3.14-slim
WORKDIR /app
COPY --from=build /venv /venv
ENV PATH="/venv/bin:$PATH" PYTHONUNBUFFERED=1
COPY app.py .
# The version is baked in at build time: docker build --build-arg APP_VERSION=1.2.0 .
ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION
# Run as a normal user, not root.
RUN useradd --uid 10001 --no-create-home appuser
USER 10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')"
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
