#!/usr/bin/env bash

ROOT="$( cd "$( dirname "$(readlink -f "$0")" )/.." >/dev/null 2>&1 && pwd )"

GITHUB_TOKEN=$(grep github_token ${ROOT}/secrets.yaml | cut -d' ' -f2)
FILES=$(grep "{GITHUB_TOKEN}" ${ROOT}/requirements.txt | sed "s/{GITHUB_TOKEN}/${GITHUB_TOKEN}/g" | tr "\r\n" " ")

[ -z "${FILES}" ] || python3 -m pip install --upgrade ${FILES}
