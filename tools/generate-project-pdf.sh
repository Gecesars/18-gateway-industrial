#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
docs_site=${EDGE18_DOCS_SITE:-/mnt/eftx-data/tools/python-docs}
output="$project_root/docs/EDGE-18-projeto-completo-rev-a.pdf"

PYTHONPATH="$docs_site${PYTHONPATH:+:$PYTHONPATH}" \
    python3 "$project_root/tools/build_project_pdf.py"
test -s "$output"
pdfinfo "$output" | grep -E '^(Pages|Page size|File size):'
