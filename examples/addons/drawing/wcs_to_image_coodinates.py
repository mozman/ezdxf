# Copyright (c) 2020, Matthew Broadway, https://github.com/mozman/ezdxf/discussions/219
# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import pathlib
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

import ezdxf
from ezdxf.math import Matrix44
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


def get_wcs_to_image_transform(
    ax: plt.Axes, image_size: tuple[int, int]
) -> Matrix44:
    """Returns the transformation matrix from modelspace coordinates to image
    coordinates.
    """
    x1, x2 = ax.get_xlim()
    y1, y2 = ax.get_ylim()
    data_width, data_height = x2 - x1, y2 - y1
    image_width, image_height = image_size
    return (
        Matrix44.translate(-x1, -y1, 0)
        @ Matrix44.scale(
            image_width / data_width, -image_height / data_height, 1.0
        )
        # +1 to counteract the effect of the pixels being flipped in y
        @ Matrix44.translate(0, image_height + 1, 0)
    )


def get_image_to_wcs_transform(
    ax: plt.Axes, image_size: tuple[int, int]
) -> Matrix44:
    """Returns the transformation matrix from image coordinates to modelspace
    coordinates.
    """
    m = get_wcs_to_image_transform(ax, image_size)
    m.inverse()
    return m


def main():
    # create the DXF document
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (1, 0), (1, 1), (0, 1)], close=True)
    msp.add_line((0, 0), (1, 1))

    # export the pixel image
    fig: plt.Figure = plt.figure()
    ax: plt.Axes = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp, finalize=True)
    fig.savefig(CWD / "cad.png")
    plt.close(fig)

    # reload the pixel image by Pillow (PIL)
    img = Image.open(CWD / "cad.png")
    draw = ImageDraw.Draw(img)

    # add some annotations to the pixel image by using modelspace coordinates
    m = get_wcs_to_image_transform(ax, img.size)
    a, b, c = (
        (v.x, v.y)  # draw.line() expects tuple[float, float] as coordinates
        # transform modelspace coordinates to image coordinates
        for v in m.transform_vertices([(0.25, 0.75), (0.75, 0.25), (1, 1)])
    )
    draw.line([a, b, c, a], fill=(255, 0, 0))

    # show the image by the default image viewer
    img.show()

    # convert pixel coordinates to modelspace coordinates
    img2wcs = get_image_to_wcs_transform(ax, img.size)
    print(f"0.25, 0.75 == {img2wcs.transform(a).round(2)}")
    print(f"0.75, 0.25 == {img2wcs.transform(b).round(2)}")
    print(f"1.00, 1.00 == {img2wcs.transform(c).round(2)}")


if __name__ == "__main__":
    main()
