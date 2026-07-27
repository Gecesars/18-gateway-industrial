#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
tool_root=${EDGE18_TOOL_ROOT:-/mnt/eftx-data/cache/antenna-coupler-tools}
kicad_root="$tool_root/kicad/root"
xvfb_root="$tool_root/xvfb/root"
wx_root="$tool_root/wx/root"

export PYTHONPATH="$wx_root/usr/lib/python3/dist-packages:$kicad_root/usr/lib/python3/dist-packages${PYTHONPATH:+:$PYTHONPATH}"
export LD_LIBRARY_PATH="$kicad_root/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PATH="$xvfb_root/usr/bin:$PATH"

exec "$xvfb_root/usr/bin/xvfb-run" -a \
    python3 "$project_root/hardware/scripts/fill_zones.py" "$@"
