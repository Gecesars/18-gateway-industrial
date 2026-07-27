#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
output="$project_root/docs/reports/edge18-rev-a.sha256"

cd "$project_root"
{
    find \
        hardware/edge18-main \
        hardware/bom \
        hardware/libraries \
        firmware/include \
        firmware/src \
        firmware/platform \
        docs/images \
        docs/reports \
        mechanical/native \
        mechanical/step \
        -type f \
        ! -name 'edge18-rev-a.sha256' \
        ! -name '*.kicad_prl' \
        ! -name '*.FCBak' \
        -print
    printf '%s\n' \
        docs/EDGE-18-projeto-completo-rev-a.pdf \
        docs/13-pinout-stm32h563-rev-a.md \
        docs/15-calculos-eletricos.md \
        docs/16-bom-e-montagem.md \
        docs/17-estado-da-pcb-rev-a.md
} | LC_ALL=C sort -u | xargs sha256sum >"$output"

test -s "$output"
echo "Generated ${output#"$project_root/"}"
