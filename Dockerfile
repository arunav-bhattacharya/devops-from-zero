# syntax=docker/dockerfile:1

# ---- build stage: a full JDK runs the Gradle wrapper ----
FROM eclipse-temurin:21-jdk AS build
WORKDIR /src

# 1. The wrapper on its own. This layer downloads Gradle itself, and Docker
#    reuses it until gradle/wrapper/gradle-wrapper.properties changes.
COPY gradlew ./
COPY gradle/wrapper/ gradle/wrapper/
RUN ./gradlew --version --no-daemon

# 2. Everything the build reads: settings, flags, catalog, build logic, both projects.
COPY settings.gradle.kts gradle.properties ./
COPY gradle/libs.versions.toml gradle/
COPY build-logic/ build-logic/
COPY greeting/ greeting/
COPY app/ app/

# 3. Compile and package. The cache mount keeps downloaded dependencies between
#    builds, even when the source code changed. Tests already ran in CI.
RUN --mount=type=cache,target=/root/.gradle/caches \
    ./gradlew --no-daemon --console=plain :app:installDist

# ---- run stage: only a JRE and the app ----
FROM eclipse-temurin:21-jre
WORKDIR /app
# installDist made bin/app (a start script) and lib/ (every jar the app needs).
COPY --from=build /src/app/build/install/app/ ./
# The version is baked in at build time: docker build --build-arg APP_VERSION=1.0.0 .
ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION
# The start script passes JAVA_OPTS to the JVM. Let the heap use up to 75%
# of the container's memory limit (the default is 25%).
ENV JAVA_OPTS="-XX:MaxRAMPercentage=75.0"
# Run as a normal user, not root.
RUN useradd --uid 10001 --no-create-home appuser
USER 10001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD curl -fsS http://localhost:8080/healthz || exit 1
# Exec form: the start script ends with exec, so the JVM becomes PID 1 and gets SIGTERM.
ENTRYPOINT ["/app/bin/app"]
