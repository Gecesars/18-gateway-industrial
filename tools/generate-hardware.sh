#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tool_root=${EDGE18_TOOL_ROOT:-/mnt/eftx-data/cache/antenna-coupler-tools}
kicad_root="$tool_root/kicad/root"
eda_site="$tool_root/python-eda/lib/python3.13/site-packages"

export KICAD_LOCAL_ROOT="$kicad_root"
export PYTHONPATH="$eda_site:$kicad_root/usr/lib/python3/dist-packages${PYTHONPATH:+:$PYTHONPATH}"
export LD_LIBRARY_PATH="$kicad_root/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

cd "$project_root"
python3 -u hardware/scripts/generate_kicad.py "$@"
