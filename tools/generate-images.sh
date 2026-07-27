#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
board="$project_root/hardware/edge18-main/edge18-main-rev-a.kicad_pcb"
schematic="$project_root/hardware/edge18-main/edge18-main-rev-a.kicad_sch"
raw="$project_root/build/visuals/raw"
images="$project_root/docs/images"
eda_site=/mnt/eftx-data/cache/antenna-coupler-tools/python-eda/lib/python3.13/site-packages

mkdir -p "$raw" "$images"
find "$raw" -mindepth 1 -delete
find "$images" -maxdepth 1 -type f -name '*.png' -delete

"$project_root/tools/kicad-cli.sh" sch export pdf \
    --output "$raw/schematic.pdf" \
    "$schematic"
pdftoppm -singlefile -png -r 180 \
    "$raw/schematic.pdf" "$raw/schematic" >/dev/null

plot_board() {
    local stem=$1
    local layers=$2
    local mirror=${3:-no}
    local mirror_arg=()
    if [[ "$mirror" == yes ]]; then
        mirror_arg+=(--mirror)
    fi
    "$project_root/tools/kicad-cli.sh" pcb export pdf \
        --output "$raw/$stem.pdf" \
        --layers "$layers" \
        --mode-single \
        --drill-shape-opt 2 \
        "${mirror_arg[@]}" \
        "$board"
    pdftoppm -singlefile -png -r 180 \
        "$raw/$stem.pdf" "$raw/$stem" >/dev/null
}

plot_board pcb-layout F.Cu,F.Mask,F.Silkscreen,Edge.Cuts
plot_board pcb-top F.Cu,Edge.Cuts
plot_board pcb-in1 In1.Cu,Edge.Cuts
plot_board pcb-in2 In2.Cu,Edge.Cuts
plot_board pcb-bottom B.Cu,Edge.Cuts yes

"$project_root/tools/kicad-cli.sh" pcb render \
    --output "$raw/pcb-3d.png" \
    --width 2400 \
    --height 1600 \
    --quality high \
    --background opaque \
    --floor \
    --perspective \
    --zoom 1.10 \
    --rotate 38,0,-28 \
    "$board"

PYTHONPATH="$eda_site${PYTHONPATH:+:$PYTHONPATH}" \
    "$project_root/tools/freecadcmd.sh" \
    -c "import runpy,sys; sys.argv=['render',r'$raw/enclosure.png']; runpy.run_path(r'$project_root/mechanical/source/render_edge18_assembly.py', run_name='__main__')"

python3 "$project_root/tools/build_visuals.py" "$raw" "$images"
