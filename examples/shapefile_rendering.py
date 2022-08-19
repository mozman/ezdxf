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
    string.digits + string.digits,
    string.punctuation,
)
RENDER_POS = 0
FRACTIONAL_ARC_SYMBOLS = "fractional_arc_symbols.shp"


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
        text_path = text_path.transform(Matrix44.translate(0, y, 0))
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
    text_path = font.render_text(text)
    path.render_splines_and_polylines(msp, [text_path])

    zoom.extents(msp)
    filename = pathlib.Path(fontname).name
    filename = CWD / filename.replace(".shp", ".text.dxf")
    doc.saveas(filename)
    print(f"created {filename}")


def debug_letter(shp_data: str, num: int, filename: str):
    font = shapefile.shp_loads(shp_data)
    doc = ezdxf.new()
    msp = doc.modelspace()
    text_path = font.render_shape(num)
    path.render_splines_and_polylines(msp, [text_path])
    zoom.extents(msp)
    doc.saveas(CWD / filename)
    print(f"created {filename}")


def render_all_chars(fontpath: pathlib.Path):
    shp_data = fontpath.read_text(encoding="latin1")
    font = shapefile.shp_loads(shp_data)
    doc = ezdxf.new()
    msp = doc.modelspace()
    numbers = list(font.shapes.keys())
    text_path = font.render_shapes(numbers)
    path.render_splines_and_polylines(msp, [text_path])
    zoom.extents(msp)
    export_path = fontpath.with_suffix(".dxf")
    doc.saveas(export_path)
    print(f"created {export_path}")


def find_fonts_with_fractional_arcs(folder: str):
    shapefile.DEBUG = True
    export_data = []
    num = 32
    for filepath in pathlib.Path(folder).glob("*.shp"):
        print("-" * 79)
        print(f"probing: {filepath}")
        shp_data = filepath.read_text(encoding="latin1")
        try:
            font = shapefile.shp_loads(shp_data)
        except shapefile.ShapeFileException as e:
            print(str(e))
            continue
        shapefile.DEBUG_SHAPE_NUMBERS.clear()
        font.render_shapes(list(font.shapes.keys()))
        if len(shapefile.DEBUG_SHAPE_NUMBERS) == 0:
            continue
        export_data.append(f";; {str(filepath)}")
        for shape_number in shapefile.DEBUG_SHAPE_NUMBERS:
            export_data.append(f";; source shape number *{shape_number:05X}")
            export_data.extend(font.shape_string(shape_number, as_num=num))
            export_data.append("")
            num += 1
    with open(CWD / FRACTIONAL_ARC_SYMBOLS, mode="wt", encoding="latin1") as fp:
        fp.write("\n".join(export_data))
    shapefile.DEBUG = False


# bold.shp letter C:
DEBUG_STR = """
*00043,156,ucc
2,8,(-2,30),5,1,
11,(0,125,0,30,044),
078,2,6,5,1,
11,(0,125,0,30,-044),
078,2,6,010,5,1,11,(0,119,0,29,044),2,6,5,1,
11,(0,119,0,29,-044),2,6,010,5,1,11,(0,114,0,28,044),2,6,5,1,
11,(0,114,0,28,-044),2,6,010,5,1,11,(0,108,0,27,044),2,6,5,1,
11,(0,108,0,27,-044),2,6,010,5,1,11,(0,102,0,26,044),2,6,5,1,
11,(0,102,0,26,-044),2,6,010,5,1,11,(0,97,0,25,044),2,6,5,1,
11,(0,97,0,25,-044),2,6,010,5,1,11,(0,90,0,24,044),2,6,5,1,
11,(0,90,0,24,-044),2,6,8,(60,-30),0
"""
DEBUG = False
if __name__ == "__main__":
    render_font("bold.shp")
    render_font("ISO.shp")
    render_font("isocp.shp")
    if DEBUG:
        find_fonts_with_fractional_arcs("C:\\Source\\shx-fonts")
        render_all_chars(CWD / FRACTIONAL_ARC_SYMBOLS)
        render_txt("bold.shp", "C")
        debug_letter(DEBUG_STR, 0x43, "bold_c.dxf")
