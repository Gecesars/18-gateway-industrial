#!/usr/bin/env python3
"""Render the FreeCAD assembly with deterministic matplotlib tessellation."""

from __future__ import annotations

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TOOL_ROOT = Path(
    os.environ.get(
        "EDGE18_TOOL_ROOT",
        "/mnt/eftx-data/cache/antenna-coupler-tools",
    )
)
sys.path.insert(
    0,
    str(TOOL_ROOT / "python-eda/lib/python3.13/site-packages"),
)
freecad_root = os.environ.get("FREECAD_LOCAL_ROOT")
if freecad_root:
    sys.path.insert(0, f"{freecad_root}/usr/lib/freecad-python3/lib")

import FreeCAD as App
import Part  # Registers Part document object types before opening FCStd.
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


MODEL = ROOT / "mechanical/native/edge18-rev-a-assembly.FCStd"


def add_shape(axis, shape, color: str, alpha: float, tolerance: float) -> None:
    vertices, facets = shape.tessellate(tolerance)
    triangles = [
        [
            (vertices[index].x, vertices[index].y, vertices[index].z)
            for index in facet
        ]
        for facet in facets
    ]
    collection = Poly3DCollection(
        triangles,
        facecolor=color,
        edgecolor="none",
        linewidth=0.0,
        alpha=alpha,
    )
    axis.add_collection3d(collection)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: render_edge18_assembly.py OUTPUT.png")
    output = Path(sys.argv[1]).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    document = App.openDocument(str(MODEL))
    figure = plt.figure(figsize=(15, 10), dpi=180)
    axis = figure.add_subplot(111, projection="3d")
    axis.set_facecolor("#eef2f7")
    figure.patch.set_facecolor("#eef2f7")

    add_shape(
        axis,
        document.getObject("EnclosureBase").Shape,
        "#a9b1bb",
        0.18,
        2.0,
    )
    add_shape(
        axis,
        document.getObject("MainPCB").Shape,
        "#13734a",
        1.0,
        1.0,
    )
    axis.set_xlim(0.0, 210.0)
    axis.set_ylim(0.0, 150.0)
    axis.set_zlim(-8.0, 70.0)
    axis.set_box_aspect((210.0, 150.0, 78.0))
    axis.view_init(elev=31.0, azim=-56.0)
    axis.set_axis_off()
    axis.set_title(
        "EDGE-18 Rev. A — PCB no gabinete aberto para trilho DIN",
        fontsize=17,
        fontweight="bold",
        color="#15243a",
        pad=18,
    )
    figure.tight_layout()
    figure.savefig(output, bbox_inches="tight", pad_inches=0.08)
    plt.close(figure)
    App.closeDocument(document.Name)
    print(f"Rendered {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
