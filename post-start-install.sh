#!/usr/bin/env bash
bash "$(dirname "$(readlink -f "$0")")/agent/post-start-install.sh"
