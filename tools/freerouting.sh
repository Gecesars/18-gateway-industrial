#!/usr/bin/env bash
set -euo pipefail

tool_root=${EDGE18_TOOL_ROOT:-/mnt/eftx-data/cache/antenna-coupler-tools}
java_bin=$(find "$tool_root/java" -path '*/bin/java' -type f -print -quit)
router_jar="$tool_root/freerouting/freerouting-2.2.4.jar"

if [[ -z "$java_bin" || ! -x "$java_bin" ]]; then
    echo "JRE local não encontrado em $tool_root/java" >&2
    exit 1
fi
if [[ ! -f "$router_jar" ]]; then
    echo "Freerouting local não encontrado em $router_jar" >&2
    exit 1
fi

export FREEROUTING__GUI__ENABLED=false

exec "$java_bin" -Djava.awt.headless=true -jar "$router_jar" "$@"
