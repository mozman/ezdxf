#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Set
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
SPECIAL_CODES = "special_codes.shp"


def render_font(fontname: str):
    fontname = find_support_file(fontname, ezdxf.options.support_dirs)
    font = shapefile.readfile(fontname)
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
    filename = CWD / (filename + ".dxf")
    doc.saveas(filename)
    print(f"created {filename}")


def render_txt(fontname: str, text: str):
    fontname = find_support_file(fontname, ezdxf.options.support_dirs)
    font = shapefile.readfile(fontname)
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
    # ignore non-ascii characters in comments and names
    shp_data = fontpath.read_text(errors="ignore")
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


def find_fonts_with_codes(folder: str, codes: Set[int]):
    shapefile.DEBUG = True
    shapefile.DEBUG_CODES = set(codes)
    export_data = []
    num = 32
    for filepath in pathlib.Path(folder).glob("*.shp"):
        print("-" * 79)
        print(f"probing: {filepath}")
        # ignore non-ascii characters in comments and names
        shp_data = filepath.read_text(errors="ignore")
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
    with open(CWD / SPECIAL_CODES, mode="wt", encoding="cp1252") as fp:
        fp.write("\n".join(export_data))
    shapefile.DEBUG = False


# bold.shp letter C:
DEBUG_UCC = """
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
DEBUG_UCR = """*00052,259,ucr
060,8,(0,28),2,064,1,8,(0,20),8,(22,0),10,(10,-024),8,(-22,0),2,
06C,1,8,(23,0),10,(6,-022),8,(1,-18),11,(0,97,0,14,041),3,2,0D0,
4,2,11,(85,0,0,8,-051),8,(-1,18),11,(0,15,0,12,002),
11,(199,0,0,16,064),8,(-28,0),8,(0,-60),2,012,1,8,(0,58),
8,(27,0),11,(0,85,0,15,-024),11,(205,0,0,11,-022),8,(1,-18),5,
11,(0,148,0,9,041),2,6,018,1,5,11,(0,136,0,10,041),2,6,018,1,5,
11,(0,119,0,11,041),2,6,018,1,5,11,(0,108,0,12,041),2,6,018,1,5,
11,(0,102,0,13,041),2,6,1,8,(-1,18),10,(7,002),8,(-24,0),
8,(0,-28),048,2,012,1,8,(0,56),8,(26,0),11,(0,131,0,14,-024),
11,(142,0,0,10,-022),8,(1,-18),2,028,1,8,(-1,18),10,(8,002),
8,(-25,0),8,(0,-28),028,2,012,1,8,(0,54),8,(25,0),10,(13,-024),5,
010,10,(9,-022),8,(1,-18),6,8,(-25,0),2,012,1,8,(0,24),8,(24,0),
10,(12,-024),8,(-24,0),2,012,1,8,(0,22),8,(23,0),10,(11,-024),
8,(-23,0),2,8,(47,-33),0
"""
DEBUG = False
if __name__ == "__main__":
    # find_fonts_with_codes("C:\\Source\\shx-fonts", codes={7})
    render_font("symap.shx")
    render_font("bold.shx")
    render_font("ISO.shx")
    render_font("isocp.shx")
    render_txt("bold.shx", "___A_A___")
    if DEBUG:
        find_fonts_with_codes("C:\\Source\\shx-fonts", codes={11})
        render_all_chars(CWD / SPECIAL_CODES)
        render_txt("bold.shx", "R?")
        debug_letter(DEBUG_UCR, 0x43, "bold_c.dxf")
        render_all_chars(
            pathlib.Path(
                find_support_file("bold.shx", ezdxf.options.support_dirs)
            )
        )
