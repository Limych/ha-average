#!/usr/bin/env bash
# shellcheck source=/dev/null

source /opt/container/helpers/common/paths.sh


if test -d "$(GetWorkspaceName).git"; then
    echo ".git exsist in $(GetWorkspaceName), existing initializing"
    exit 1
fi

echo "Initializing dev env for integration"
rm -R /tmp/init > /dev/null 2>&1

git clone https://github.com/custom-components/integration-blueprint.git /tmp/init

rm -R /tmp/init/.git
rm -R /tmp/init/.devcontainer
cp -a /tmp/init/. "$(GetWorkspaceName)"
cd "$(GetWorkspaceName)" || exit 1
git init