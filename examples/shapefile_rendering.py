#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib
import string
import ezdxf
from ezdxf import shapefile, path, zoom
from ezdxf.math import Matrix44

# I can not include the test files in the repository because these shape files
# are generated from copyright protected Autodesk SHX files by the program dumpshx.exe
SHAPE_DIR = pathlib.Path("../DXFResearch/shx-fonts").absolute()
CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

LETTERS = (
    string.ascii_uppercase,
    string.ascii_lowercase,
    string.digits,
    string.punctuation,
)
RENDER_POS = 0


def render_font(fontname: str):
    shp_data = (SHAPE_DIR / fontname).read_text()  # the txt.shx font
    font = shapefile.shp_loads(shp_data)
    doc = ezdxf.new()
    msp = doc.modelspace()
    line_height = font.cap_height / 3 * 5
    y = RENDER_POS
    for text_line in (f"FONT: {fontname}",) + LETTERS:
        text_path = font.render_text(text_line)
        text_path = text_path.transform(
            Matrix44.translate(0, y, 0)
        )
        path.render_splines_and_polylines(msp, [text_path])
        y -= line_height

    zoom.extents(msp)
    filename = fontname.replace(".shp", ".dxf")
    doc.saveas(CWD / filename)
    print(f"created {filename}")


def render_txt(fontname: str, text: str):
    shp_data = (SHAPE_DIR / fontname).read_text()  # the txt.shx font
    font = shapefile.shp_loads(shp_data)
    doc = ezdxf.new()
    msp = doc.modelspace()
    line_height = font.cap_height / 3 * 5
    y = RENDER_POS
    text_path = font.render_text(text)
    text_path = text_path.transform(
        Matrix44.translate(0, y, 0)
    )
    path.render_splines_and_polylines(msp, [text_path])
    y -= line_height

    zoom.extents(msp)
    filename = "text-sample-" + fontname.replace(".shp", ".dxf")
    doc.saveas(CWD / filename)
    print(f"created {filename}")


if __name__ == "__main__":
    #render_font("txt.shp")
    render_font("iso.shp")
    render_font("isocp.shp")
    render_txt("isocp.shp", "&")
