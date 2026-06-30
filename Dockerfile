FROM python:trixie

RUN set -eux; \
    apt-get update; \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      ca-certificates curl git \
      git-lfs \
      libgtk2.0-0t64 \
      libgtk-3-0t64 \
      libnotify4 \
      libgbm1 \
      libnss3 \
      libxss1 \
      libasound2 \
      libxtst6 \
      xauth \
      xvfb \
      fonts-liberation \
      libayatana-appindicator3-1 \
      xdg-utils; \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry awscli

WORKDIR /nhs-notify-release-tests
COPY . .