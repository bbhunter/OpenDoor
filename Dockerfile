# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13

FROM python:${PYTHON_VERSION}-slim AS runtime

LABEL org.opencontainers.image.title="OpenDoor"
LABEL org.opencontainers.image.description="Open-source CLI scanner for authorized web reconnaissance, directory discovery, and exposure assessment."
LABEL org.opencontainers.image.source="https://github.com/stanislav-web/OpenDoor"
LABEL org.opencontainers.image.licenses="GPL-3.0-only"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    OPENDOOR_DOCKER=1

WORKDIR /opt/opendoor

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN python -m pip install --upgrade pip \
    && python -m pip install .

RUN useradd --create-home --shell /usr/sbin/nologin opendoor \
    && mkdir -p /work /opt/opendoor/reports /opt/opendoor/syslog \
    && chown -R opendoor:opendoor /work /opt/opendoor

USER opendoor

WORKDIR /work

ENTRYPOINT ["opendoor"]
CMD ["--help"]