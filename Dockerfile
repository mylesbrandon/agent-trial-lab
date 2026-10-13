# Multi-architecture manifest pinned for reproducible Linux environments.
FROM python:3.14.6-slim-bookworm@sha256:4c92ffcde4dd6f1ff72a24518f49fd4990b27134987dfa31a733badde66df9f8

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.txt \
    && groupadd --gid 10001 benchmark \
    && useradd --uid 10001 --gid 10001 --no-create-home benchmark
COPY runner/ ./runner/
COPY tasks/ ./tasks/
COPY results/candidates/reference/ ./results/candidates/reference/
COPY results/baselines/ ./results/baselines/
USER 10001:10001
ENTRYPOINT ["python", "-m", "runner.container_workflow"]
