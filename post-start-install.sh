#!/usr/bin/env bash
# Runs after the EFS home mounts. Make the per-box Claude app folder first (see agent/install.sh step 6).
mkdir -p "$HOME/.claude-remote-local" && chmod 700 "$HOME/.claude-remote-local"
bash "$(dirname "$(readlink -f "$0")")/agent/post-start-install.sh"
