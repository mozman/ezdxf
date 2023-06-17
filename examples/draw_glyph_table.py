#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
#  https://en.wikipedia.org/wiki/Unicode_font
import sys
import argparse

import ezdxf
from ezdxf import path
from ezdxf.math import Matrix44
from ezdxf.fonts import fonts
from ezdxf.layouts import Layout
import pathlib

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

CAP_HEIGHT = 2
SQUARE_SIZE = 6
GLYPH_OFFSET = 2


def render_glyph_table(font: fonts.TrueTypeFont, layout: Layout):
    text_attribs = {
        "layer": "TEXT",
        "style": "TEXT",
        "height": CAP_HEIGHT,
    }
    glyph_attribs = {
        "layer": "GLYPH",
    }
    red_dot_attribs = {
        "layer": "DOTS",
    }
    undef_path = font.text_path(chr(0))
    undef_hash = hash(tuple(undef_path.control_vertices()))
    half_height = CAP_HEIGHT / 2
    for page in range(256):
        insert_y = page * SQUARE_SIZE + GLYPH_OFFSET
        _page = page << 8
        label = f"{_page:04x}"
        print(f"rendering page: {label}")
        layout.add_text(label, dxfattribs=text_attribs).set_placement((-10, insert_y))
        for code in range(256):
            insert_x = SQUARE_SIZE * code + GLYPH_OFFSET
            code_point = (page << 8) + code
            glyph = font.text_path(chr(code_point))
            if undef_hash == hash(tuple(glyph.control_vertices())):
                layout.add_point(
                    (insert_x + half_height, insert_y + half_height),
                    dxfattribs=red_dot_attribs,
                )
                continue
            m = Matrix44.translate(insert_x, insert_y, 0)
            glyph.transform_inplace(m)
            path.render_hatches(layout, [glyph.to_path()], dxfattribs=glyph_attribs)


def render_font(font_name: str, sideload: bool):
    doc = ezdxf.new()
    doc.layers.add("TEXT")
    doc.layers.add("GLYPH")
    doc.layers.add("DOTS", color=1)
    doc.styles.add("TEXT", font="Arial.ttf")
    msp = doc.modelspace()
    if sideload:
        font = fonts.sideload_ttf(font_name, CAP_HEIGHT)
    else:
        font = fonts.make_font(font_name, CAP_HEIGHT)
    if font.name != font_name:
        print(f"font '{font_name}' not found.")
        exit(1)
    render_glyph_table(font, msp)  # type: ignore
    size = 260 * SQUARE_SIZE
    doc.set_modelspace_vport(size, center=(size / 2, size / 2))
    out_name = pathlib.Path(font_name).name.replace('.', '_')
    file_path = CWD / f"glyph_table_{out_name}.dxf"
    print(f"writing: {file_path}")
    doc.saveas(file_path)
    print("done")


def main():
    parser = argparse.ArgumentParser(
        __file__,
    )
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="+",
        help="font file name to render",
    )
    parser.add_argument(
        "-s",
        "--sideload",
        action="store_true",
        default=False,
        help="bypass the font manager and load a font straight from disk, requires an absolute file path",
    )
    args = parser.parse_args(sys.argv[1:])

    for font_name in args.files:
        render_font(font_name, args.sideload)


if __name__ == "__main__":
    main()
