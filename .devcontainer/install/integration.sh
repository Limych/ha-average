#!/usr/bin/env bash
set -e
echo -e "\\033[0;34mRunning install script 'integration.sh'\\033[0m"

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    ffmpeg \
    gcc \
    git \
    jq \
    libavcodec-dev \
    libavdevice-dev \
    libavfilter-dev \
    libavformat-dev \
    libavutil-dev \
    libbz2-dev \
    libcap-dev \
    libffi-dev \
    libjpeg-dev \
    liblzma-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libpcap-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libswresample-dev \
    libswscale-dev \
    llvm \
    shellcheck \
    tar \
    tk-dev \
    wget \
    xz-utils \
    zlib1g-dev

python3 -m pip --disable-pip-version-check install --upgrade \
    git+https://github.com/home-assistant/home-assistant.git@dev
python3 -m pip --disable-pip-version-check install --upgrade wheel setuptools

# Fix issue https://github.com/home-assistant/core/issues/95192
python3 -m pip --disable-pip-version-check install --upgrade git+https://github.com/boto/botocore urllib3~=1.26
