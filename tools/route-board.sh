#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
tool_root=${EDGE18_TOOL_ROOT:-/mnt/eftx-data/cache/antenna-coupler-tools}
kicad_root="$tool_root/kicad/root"
eda_site="$tool_root/python-eda/lib/python3.13/site-packages"
route_dir="$project_root/build/freerouting"
board="$project_root/hardware/edge18-main/edge18-main-rev-a.kicad_pcb"
dsn="$route_dir/edge18-main-rev-a.dsn"
ses="$route_dir/edge18-main-rev-a.ses"
passes=${1:-1}

if ! [[ "$passes" =~ ^[1-9][0-9]*$ ]]; then
    echo "usage: $0 [positive-pass-count]" >&2
    exit 2
fi

export PYTHONPATH="$eda_site:$kicad_root/usr/lib/python3/dist-packages${PYTHONPATH:+:$PYTHONPATH}"
export LD_LIBRARY_PATH="$kicad_root/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

mkdir -p "$route_dir"
python3 "$project_root/hardware/scripts/sanitize_board.py" "$board"
python3 "$project_root/hardware/scripts/specctra_io.py" export "$board" "$dsn"
"$project_root/tools/freerouting.sh" \
    -de "$dsn" \
    -do "$ses" \
    -l en \
    -mp "$passes" \
    --gui.enabled=false \
    --router.optimizer.enabled=false
python3 "$project_root/hardware/scripts/specctra_io.py" import "$board" "$ses"
python3 "$project_root/hardware/scripts/sanitize_board.py" "$board"
"$project_root/tools/fill-zones.sh" "$board"

echo "PCB roteado com $passes passe(s) e planos recalculados: $board"
