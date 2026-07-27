#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
board="$project_root/hardware/edge18-main/edge18-main-rev-a.kicad_pcb"
schematic="$project_root/hardware/edge18-main/edge18-main-rev-a.kicad_sch"
release="$project_root/release/edge18-rev-a"
gerbers="$release/gerbers"
documents="$release/documents"
assembly="$release/assembly"
mechanical="$release/mechanical"

mkdir -p "$release"
find "$release" -mindepth 1 -delete
mkdir -p "$gerbers" "$documents" "$assembly" "$mechanical"

"$project_root/tools/kicad-cli.sh" sch erc \
    --exit-code-violations \
    --output "$documents/edge18-main-rev-a-erc.rpt" \
    "$schematic"
"$project_root/tools/kicad-cli.sh" pcb drc \
    --exit-code-violations \
    --output "$documents/edge18-main-rev-a-drc.rpt" \
    "$board"

"$project_root/tools/kicad-cli.sh" sch export pdf \
    --output "$documents/edge18-main-rev-a-schematic.pdf" \
    "$schematic"
"$project_root/tools/kicad-cli.sh" pcb export pdf \
    --output "$documents/edge18-main-rev-a-assembly.pdf" \
    --layers F.Fab,B.Fab,Edge.Cuts \
    --mode-multipage \
    --sketch-pads-on-fab-layers \
    --crossout-DNP-footprints-on-fab-layers \
    "$board"
"$project_root/tools/kicad-cli.sh" pcb export gerbers \
    --output "$gerbers" \
    --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts \
    --precision 6 \
    "$board"
"$project_root/tools/kicad-cli.sh" pcb export drill \
    --output "$gerbers" \
    --format excellon \
    --excellon-units mm \
    --excellon-separate-th \
    --generate-map \
    --map-format pdf \
    "$board"
"$project_root/tools/kicad-cli.sh" pcb export ipcd356 \
    --output "$assembly/edge18-main-rev-a.ipc" \
    "$board"
"$project_root/tools/kicad-cli.sh" pcb export pos \
    --output "$assembly/edge18-main-rev-a-position.csv" \
    --format csv \
    --units mm \
    --side both \
    --exclude-dnp \
    "$board"
"$project_root/tools/kicad-cli.sh" pcb export step \
    --output "$mechanical/edge18-main-rev-a.step" \
    --force \
    --subst-models \
    --no-dnp \
    "$board"

cp "$project_root/hardware/bom/edge18-main-rev-a-source.csv" \
    "$assembly/edge18-main-rev-a-bom-source.csv"
python3 "$project_root/hardware/scripts/group_bom.py" \
    "$project_root/hardware/bom/edge18-main-rev-a-source.csv" \
    "$assembly/edge18-main-rev-a-bom-grouped.csv"

(
    cd "$release"
    find gerbers documents assembly mechanical \
        -type f -print0 \
        | sort -z \
        | xargs -0 sha256sum > manifest.sha256
)
rm -f "$project_root/release/edge18-rev-a.zip"
(
    cd "$project_root/release"
    zip -q -r edge18-rev-a.zip edge18-rev-a
)

echo "Release package exported to $release"
