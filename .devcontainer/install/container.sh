#!/usr/bin/env bash
set -e
echo -e "\\033[0;34mRunning install script 'container.sh'\\033[0m"

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends \
    make

mkdir -p /opt/container/makefiles
mkdir -p /opt/container/helpers
touch /opt/container/makefiles/dummy.mk

cp /container/container.mk /opt/container/container.mk
cp -r /container/helpers/common /opt/container/helpers/common

cp /container/container /usr/bin/container
chmod +x /usr/bin/container

cp /container/makefiles/integration.mk /opt/container/makefiles/integration.mk
cp -r /container/helpers/integration /opt/container/helpers/integration

container help
