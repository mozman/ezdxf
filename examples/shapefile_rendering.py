#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib
import string
import ezdxf
from ezdxf import shapefile, path, zoom
from ezdxf.math import Matrix44
from ezdxf.filemanagement import find_support_file

# I can not include the test files in the repository because these shape files
# are generated from copyright protected Autodesk SHX files by the program dumpshx.exe
# Add the directory containing the shx/shp files to your config file:
# 1. create a default config file in home directory at ~/.config/ezdxf/ezdxf.ini
#
#     $ ezdxf config --home
#
# 2. add the font directory as support dir, this is my config file:
# [core]
# default_dimension_text_style = OpenSansCondensed-Light
# test_files = ~/src/dxftest
# font_cache_directory =
# support_dirs = ~/src/shx-fonts
# 	~/src/ctb
# ...

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

LETTERS = (
    string.ascii_uppercase,
    string.ascii_lowercase,
    string.digits+string.digits,
    string.punctuation,
)
RENDER_POS = 0


def render_font(fontname: str):
    fontname = find_support_file(fontname, ezdxf.options.support_dirs)
    shp_data = pathlib.Path(fontname).read_text(encoding="latin1")
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
    filename = pathlib.Path(fontname).name
    filename = CWD / filename.replace(".shp", ".dxf")
    doc.saveas(filename)
    print(f"created {filename}")


def render_txt(fontname: str, text: str):
    fontname = find_support_file(fontname, ezdxf.options.support_dirs)
    shp_data = pathlib.Path(fontname).read_text(encoding="latin1")
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
    filename = pathlib.Path(fontname).name
    filename = CWD / filename.replace(".shp", ".text.dxf")
    doc.saveas(filename)
    print(f"created {filename}")


if __name__ == "__main__":
    render_font("txt.shp")
    render_font("ISO.shp")
    render_font("isocp.shp")
    render_txt("isocp.shp", "A&99&A")
