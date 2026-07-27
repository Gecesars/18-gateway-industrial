#!/usr/bin/env bash
set -euo pipefail

tool_root=${EDGE18_TOOL_ROOT:-/mnt/eftx-data/cache/antenna-coupler-tools}
freecad_root="$tool_root/freecad/root"

export FREECAD_LOCAL_ROOT="$freecad_root"
export PYTHONPATH="$freecad_root/usr/lib/freecad-python3/lib:$freecad_root/usr/lib/python3/dist-packages${PYTHONPATH:+:$PYTHONPATH}"
export LD_LIBRARY_PATH="$freecad_root/usr/lib/x86_64-linux-gnu:$freecad_root/usr/lib/freecad-python3/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

if command -v bwrap >/dev/null 2>&1; then
    user_root="$tool_root/freecad/edge18-user"
    mkdir -p "$user_root/config" "$user_root/data" "$user_root/cache"
    exec bwrap \
        --ro-bind / / \
        --dev-bind /dev /dev \
        --proc /proc \
        --bind /mnt/eftx-data /mnt/eftx-data \
        --bind /tmp /tmp \
        --tmpfs /usr/share \
        --ro-bind "$freecad_root/usr/share/freecad" /usr/share/freecad \
        --ro-bind /usr/share/fonts /usr/share/fonts \
        --ro-bind /usr/share/fontconfig /usr/share/fontconfig \
        --setenv FREECAD_LOCAL_ROOT "$FREECAD_LOCAL_ROOT" \
        --setenv PYTHONPATH "$PYTHONPATH" \
        --setenv LD_LIBRARY_PATH "$LD_LIBRARY_PATH" \
        --setenv XDG_CONFIG_HOME "$user_root/config" \
        --setenv XDG_DATA_HOME "$user_root/data" \
        --setenv XDG_CACHE_HOME "$user_root/cache" \
        "$freecad_root/usr/lib/freecad/bin/freecadcmd-python3" "$@"
fi

exec "$freecad_root/usr/lib/freecad/bin/freecadcmd-python3" "$@"
