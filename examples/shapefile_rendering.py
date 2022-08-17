#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf
from ezdxf import shapefile, path, zoom

# I can not include the test files in the repository because these shape files
# are generated from copyright protected Autodesk SHX files by the program dumpshx.exe
SHAPE_DIR = pathlib.Path("../DXFResearch/SHX").absolute()
CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


def render_txt(filename):
    txt_shp = (SHAPE_DIR / "txt.shp").read_text()  # the txt.shx font
    txt_font = shapefile.shp_loads(txt_shp)
    doc = ezdxf.new()
    msp = doc.modelspace()
    text_path = txt_font.render_text("ABCDEF")
    path.render_splines_and_polylines(msp, [text_path])

    zoom.extents(msp)
    doc.saveas(CWD / filename)


if __name__ == '__main__':
    render_txt("txt_font.dxf")


