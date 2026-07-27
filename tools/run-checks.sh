#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
build_root="$project_root/build/host"

python3 -m json.tool "$project_root/schemas/gateway-config.schema.json" >/dev/null
python3 -m json.tool "$project_root/schemas/telemetry.schema.json" >/dev/null
python3 -m json.tool "$project_root/examples/gateway-config.example.json" >/dev/null
python3 -m json.tool "$project_root/examples/telemetry.example.json" >/dev/null
python3 "$project_root/tools/validate_schemas.py"
python3 "$project_root/tools/check_doc_links.py"

cmake -S "$project_root" -B "$build_root" -DCMAKE_BUILD_TYPE=Debug
cmake --build "$build_root"
ctest --test-dir "$build_root" --output-on-failure

if test -f "$project_root/mechanical/native/edge18-p0-assembly.FCStd"; then
    validator="$project_root/mechanical/source/validate_edge18_enclosure.py"
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
fi

if rg -n '[[:blank:]]+$' \
    "$project_root/README.md" \
    "$project_root/docs" \
    "$project_root/firmware" \
    "$project_root/project-management" \
    "$project_root/schemas" \
    "$project_root/examples"; then
    echo "Trailing whitespace detected" >&2
    exit 1
fi

echo "EDGE-18 checks: PASS"
