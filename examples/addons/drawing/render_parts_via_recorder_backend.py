#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from typing import Iterator
import pathlib
import random

import ezdxf
from ezdxf.addons.drawing import (
    RenderContext,
    Frontend,
    recorder,
    config,
    layout,
    pymupdf,
)
from ezdxf.math import BoundingBox2d

# ------------------------------------------------------------------------------
# This example renders the DXF file in rows by cols tiles including filtering
# the DXF entities outside the rendering area.
#
# This example is a reimplementation of the "render_model_space_as_tiles.py" example
# nut uses the new RecorderBackend introduced in ezdxf v1.1.
# The RecorderBackend stores the output of the Frontend as compact objects based on
# numpy arrays.  The recordings can be replayed on any other backend, including the
# older Matplotlib- and PyQt backends.  The player class provides fast bounding box
# detection, inplace transformation and rectangular content cropping.
#
# docs: https://ezdxf.mozman.at/docs/addons/drawing.html
# ------------------------------------------------------------------------------

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

COLORS = list(range(1, 7))
WIDTH = 400
HEIGHT = 400


def random_points(count: int, width: float, height: float):
    for _ in range(count):
        yield width * random.random(), height * random.random()


def create_content(msp):
    for s, e in zip(
        random_points(100, WIDTH, HEIGHT), random_points(100, WIDTH, HEIGHT)
    ):
        msp.add_line(s, e, dxfattribs={"color": random.choice(COLORS)})


def render_areas(extents, grid=(2, 2)) -> Iterator[BoundingBox2d]:
    """Returns a bounding box for each tile to render."""
    rows, cols = grid
    tile_width = extents.size.x / cols
    tile_height = extents.size.y / rows
    for row in range(rows):
        for col in range(cols):
            x_min = extents.extmin.x + col * tile_width
            y_min = extents.extmin.y + row * tile_height
            # BoundingBox2d ignores the z-axis!
            yield BoundingBox2d(
                [(x_min, y_min), (x_min + tile_width, y_min + tile_height)]
            )


def main(rows: int, cols: int):
    doc = ezdxf.new()
    msp = doc.modelspace()
    create_content(msp)

    ctx = RenderContext(doc)
    # record the output of the Frontend class
    recorder_backend = recorder.Recorder()
    Frontend(
        ctx,
        recorder_backend,
        config=config.Configuration(background_policy=config.BackgroundPolicy.WHITE),
    ).draw_layout(msp)

    # the main player has access to the original recordings
    main_player = recorder_backend.player()
    # basic layout settings for full image and all tiles
    settings = layout.Settings(fit_page=False)

    # export full image
    # always copy the main player when the content is rendered multiple times!
    full_player = main_player.copy()
    # create the output backend
    png_backend = pymupdf.PyMuPdfBackend()
    full_player.replay(png_backend)
    # export full image as png file, auto-detect image size
    page = layout.Page(0, 0, layout.Units.mm)
    (CWD / "full_image.png").write_bytes(
        png_backend.get_pixmap_bytes(page, settings=settings)
    )
    # calculating tile size:
    extents = full_player.bbox()
    image_size = extents.size
    tile_size_x = image_size.x / cols
    tile_size_y = image_size.y / rows

    # export image as tiles
    for tile, render_area in enumerate(render_areas(extents, (rows, cols))):
        # copy the content of the main player!!!
        tile_player = main_player.copy()
        # crop content to the size of the tile
        tile_player.crop_rect(render_area.extmin, render_area.extmax, distance=0.1)
        # create a new output backend for each tile
        png_backend = pymupdf.PyMuPdfBackend()
        tile_player.replay(png_backend)
        filename = f"tile-{tile:02d}.png"
        print(f'saving tile #{tile} to "{filename}"')
        # export tile as png file
        page = layout.Page(tile_size_x, tile_size_y, layout.Units.mm)
        (CWD / filename).write_bytes(
            png_backend.get_pixmap_bytes(
                page, fmt="png", settings=settings, render_box=render_area
            )
        )


if __name__ == "__main__":
    # create 3x3 tiles
    main(3, 3)
