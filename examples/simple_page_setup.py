#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pathlib
import ezdxf
from ezdxf.layouts import Paperspace

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to use the simple page setup method of the Drawing object.
#
# This setup creates simple layouts without margins and offset, this way changing
# the output device is easy at least is BricsCAD.
# ------------------------------------------------------------------------------


def draw_crossings_lines(psp: Paperspace):
    # These layouts have no margins and offset defined, so the drawing space is
    # the whole sheet, but printers and plotters will not print to the
    # border of the sheet! In real world files keep always a safety space between
    # the sheet borders and the content. The size of that safety space cannot be
    # known because it's different for each printer and plotter.
    width = psp.dxf.paper_width
    height = psp.dxf.paper_height
    psp.add_line((0, 0), (width, height))
    psp.add_line((0, height), (width, 0))


def main():
    doc = ezdxf.new()
    layout1 = doc.page_setup("Layout1", "ISO A0", landscape=True)
    layout2 = doc.page_setup("Layout2", "ISO A0", landscape=False)
    draw_crossings_lines(layout1)
    draw_crossings_lines(layout2)
    doc.saveas(CWD / "simple_page_setup.dxf")


if __name__ == "__main__":
    main()
