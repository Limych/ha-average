#!/usr/bin/env bash

function workspacePath {
    if [[ -n "$WORKSPACE_DIRECTORY" ]]; then
        echo "${WORKSPACE_DIRECTORY}/"
    else
        echo "$(find /workspaces -mindepth 1 -maxdepth 1 -type d | tail -1)/"
    fi
}