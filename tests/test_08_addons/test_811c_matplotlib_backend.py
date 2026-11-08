# Copyright (c) 2026, Manfred Moitzi
# License: MIT License

from types import SimpleNamespace

import pytest

pytest.importorskip("matplotlib")
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from ezdxf import path
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.pipeline import RenderPipeline2d
from ezdxf.addons.drawing.properties import Properties
from ezdxf.math import Matrix44
from ezdxf.npshapes import NumpyPath2d


def test_filled_text_preserves_glyph_winding():
    # Nested same-direction contours stay filled. Hole detection punches them out.
    glyph = path.Path()
    for vertices in (
        [(0, 0), (8, 0), (8, 8), (0, 8)],
        [(2, 2), (6, 2), (6, 6), (2, 6)],
    ):
        glyph.extend_multi_path(path.from_vertices(vertices, close=True))

    figure = Figure(figsize=(4, 4), dpi=100)
    canvas = FigureCanvasAgg(figure)
    ax = figure.add_axes((0, 0, 1, 1))
    pipeline = RenderPipeline2d(MatplotlibBackend(ax, adjust_figure=False))
    pipeline.text_engine = SimpleNamespace(
        get_text_glyph_paths=lambda *args: [NumpyPath2d(glyph)],
        is_stroke_font=lambda face: False,
    )
    properties = Properties()
    properties.color = "#000000"
    pipeline.draw_text("A", Matrix44(), properties, 1)
    ax.set_xlim(-1, 9)
    ax.set_ylim(-1, 9)
    canvas.draw()
    image = canvas.buffer_rgba()
    x, y = (int(v) for v in ax.transData.transform((4, 4)))
    assert image[image.shape[0] - 1 - y, x, 0] < 32
