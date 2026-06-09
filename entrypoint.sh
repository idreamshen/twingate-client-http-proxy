#!/bin/sh
set -eu

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

printf 'y\n' | twingate config networking "http-proxy=${TWINGATE_HTTP_PROXY}" "tun=${TWINGATE_TUN}" 2>/dev/null || true

exec python3 /usr/local/share/twingate-webui/server.py
