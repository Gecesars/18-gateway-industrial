#!/usr/bin/env bash
set -euo pipefail

tool_root=${EDGE18_TOOL_ROOT:-/mnt/eftx-data/cache/antenna-coupler-tools}
kicad_root="$tool_root/kicad/root"

export LD_LIBRARY_PATH="$kicad_root/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export KICAD9_SYMBOL_DIR="$kicad_root/usr/share/kicad/symbols"
export KICAD9_FOOTPRINT_DIR="$kicad_root/usr/share/kicad/footprints"
export KICAD9_3DMODEL_DIR="$kicad_root/usr/share/kicad/3dmodels"

if command -v bwrap >/dev/null 2>&1; then
    config_root="$tool_root/kicad/edge18-user"
    mkdir -p "$config_root/config" "$config_root/cache"
    exec bwrap \
        --ro-bind / / \
        --dev-bind /dev /dev \
        --proc /proc \
        --bind /mnt/eftx-data /mnt/eftx-data \
        --bind /tmp /tmp \
        --tmpfs /usr/share \
        --ro-bind "$kicad_root/usr/share/kicad" /usr/share/kicad \
        --ro-bind /usr/share/fonts /usr/share/fonts \
        --ro-bind /usr/share/fontconfig /usr/share/fontconfig \
        --setenv LD_LIBRARY_PATH "$LD_LIBRARY_PATH" \
        --setenv KICAD9_SYMBOL_DIR "$KICAD9_SYMBOL_DIR" \
        --setenv KICAD9_FOOTPRINT_DIR "$KICAD9_FOOTPRINT_DIR" \
        --setenv KICAD9_3DMODEL_DIR "$KICAD9_3DMODEL_DIR" \
        --setenv XDG_CONFIG_HOME "$config_root/config" \
        --setenv XDG_CACHE_HOME "$config_root/cache" \
        "$kicad_root/usr/bin/kicad-cli" "$@"
fi

exec "$kicad_root/usr/bin/kicad-cli" "$@"
