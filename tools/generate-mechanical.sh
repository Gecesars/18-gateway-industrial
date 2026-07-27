#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
generator="$project_root/mechanical/source/generate_edge18_enclosure.py"
validator="$project_root/mechanical/source/validate_edge18_enclosure.py"

generator_output=$(
    "$project_root/tools/freecadcmd.sh" \
        -c "import runpy; runpy.run_path(r'$generator', run_name='__main__')" \
        2>&1
)
printf '%s\n' "$generator_output"
if ! grep -Fq "Generated EDGE-18 FreeCAD and STEP artifacts" \
    <<<"$generator_output"; then
    echo "FreeCAD generation did not reach its success marker" >&2
    exit 1
fi

for artifact in \
    "$project_root/mechanical/native/edge18-p0-assembly.FCStd" \
    "$project_root/mechanical/step/edge18-p0-enclosure-base.step" \
    "$project_root/mechanical/step/edge18-p0-enclosure-lid.step" \
    "$project_root/mechanical/step/edge18-p0-assembly.step"; do
    if ! test -s "$artifact"; then
        echo "Missing or empty mechanical artifact: $artifact" >&2
        exit 1
    fi
done

validator_output=$(
    "$project_root/tools/freecadcmd.sh" \
        -c "import runpy; runpy.run_path(r'$validator', run_name='__main__')" \
        2>&1
)
printf '%s\n' "$validator_output"
if ! grep -Fq "EDGE-18 mechanical validation: PASS" \
    <<<"$validator_output"; then
    echo "FreeCAD validation did not reach its success marker" >&2
    exit 1
fi
