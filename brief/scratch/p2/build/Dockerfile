# Start from a small official Python image.
FROM python:3.14-slim

# Work in /app inside the image. Docker creates the folder.
WORKDIR /app

# Copy the dependency list first, so the slow install step is cached.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the code. Editing app.py only rebuilds from here down.
COPY app.py .

# The version is set at build time: docker build --build-arg APP_VERSION=1.0.0 .
ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION PYTHONUNBUFFERED=1

# Document the port the app listens on. This does not publish it.
EXPOSE 8000

# Start gunicorn on all interfaces, port 8000.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
