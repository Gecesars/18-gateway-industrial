#!/usr/bin/env python3
"""Remove sub-micron router artifacts that collapse in DSN precision."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pcbnew


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Path)
    args = parser.parse_args()
    board_path = args.board.resolve()
    board = pcbnew.LoadBoard(str(board_path))
    removed = 0

    for track in list(board.GetTracks()):
        if isinstance(track, pcbnew.PCB_VIA):
            continue
        # Specctra uses a coarser integer grid than KiCad. Short endpoint
        # correction segments emitted by the first route pass can collapse to
        # one point when a routed SES is exported again. Removing segments
        # below 0.10 mm lets the next pass reconnect the same pad cleanly and
        # avoids Freerouting's insert_forced_trace_polyline crash.
        if pcbnew.ToMM(track.GetLength()) < 0.100:
            board.Remove(track)
            removed += 1
    pcbnew.SaveBoard(str(board_path), board)
    print(f"Removed {removed} short route artifacts", flush=True)
    # Avoid the known KiCad 9 SWIG destructor crash after removing tracks.
    os._exit(0)


if __name__ == "__main__":
    raise SystemExit(main())
