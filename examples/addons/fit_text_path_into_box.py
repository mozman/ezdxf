#  Copyright (c) 2021-2022, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf
from ezdxf import path, zoom
from ezdxf.math import Matrix44
from ezdxf.tools import fonts
from ezdxf.addons import text2path

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how create outline paths from a text and fit them into a
# specified rectangle.
# ------------------------------------------------------------------------------


def main():
    doc = ezdxf.new()
    msp = doc.modelspace()

    ff = fonts.FontFace(family="Arial")
    box_width, box_height = 4, 2

    # Draw the target box:
    msp.add_lwpolyline(
        [(0, 0), (box_width, 0), (box_width, box_height), (0, box_height)],
        close=True,
        dxfattribs={"color": 1},
    )

    # Convert text string into path objects:
    text_as_paths = text2path.make_paths_from_str("Squeeze Me", ff)

    # Fit text paths into a given box size by scaling, does not move the path
    # objects:
    # - uniform=True, keeps the text aspect ratio
    # - uniform=False, scales the text to touch all 4 sides of the box
    final_paths = path.fit_paths_into_box(
        text_as_paths, size=(box_width, box_height, 0), uniform=False
    )

    # Mirror text about the x-axis
    final_paths = path.transform_paths(final_paths, Matrix44.scale(-1, 1, 1))

    # Move bottom/left corner to (0, 0) if required:
    bbox = path.bbox(final_paths)
    dx, dy, dz = -bbox.extmin
    final_paths = path.transform_paths(
        final_paths, Matrix44.translate(dx, dy, dz)
    )

    path.render_lwpolylines(
        msp, final_paths, distance=0.01, dxfattribs={"color": 2}
    )

    zoom.extents(msp)
    doc.saveas(CWD / "SqueezeMe.dxf")


if __name__ == "__main__":
    main()
