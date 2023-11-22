#!/usr/bin/env bash

read -p 'Set Home Assistant version: ' -r version
python3 -m pip --disable-pip-version-check install --upgrade homeassistant=="$version"

if [[ -n "$POST_SET_VERSION_HOOK" ]]; then
    "$POST_SET_VERSION_HOOK" "$version"
fi