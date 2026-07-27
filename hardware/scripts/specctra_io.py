#!/usr/bin/env python3
"""Export a KiCad board to DSN or import a routed SES session."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pcbnew


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("export", "import"))
    parser.add_argument("board", type=Path)
    parser.add_argument("exchange", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    board_path = args.board.resolve()
    exchange_path = args.exchange.resolve()
    board = pcbnew.LoadBoard(str(board_path))

    if args.operation == "export":
        # The native zones remain in the source PCB. Removing them only from
        # the in-memory DSN export makes every connection explicit to the
        # router and avoids treating isolated copper islands as completed nets.
        for zone in list(board.Zones()):
            board.Remove(zone)
        exchange_path.parent.mkdir(parents=True, exist_ok=True)
        if not pcbnew.ExportSpecctraDSN(board, str(exchange_path)):
            raise RuntimeError(f"falha ao exportar {exchange_path}")
        # KiCad 9's SWIG bindings may crash while destroying the temporary
        # zone objects at interpreter shutdown. The DSN is fully flushed here;
        # exiting without the faulty C++ destructor keeps the CLI deterministic.
        os._exit(0)
    else:
        if not pcbnew.ImportSpecctraSES(board, str(exchange_path)):
            raise RuntimeError(f"falha ao importar {exchange_path}")
        pcbnew.SaveBoard(str(board_path), board)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
