#!/usr/bin/env python3
"""Refill all copper zones and save the KiCad board."""

from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew
import wx


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Path)
    args = parser.parse_args()

    # KiCad's zone filler queries the display geometry through wxWidgets.
    # The shell wrapper supplies a private headless X display.
    app = wx.App(False)
    board_path = args.board.resolve()
    board = pcbnew.LoadBoard(str(board_path))
    for zone in board.Zones():
        zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones(), False)
    pcbnew.SaveBoard(str(board_path), board)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
