#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

from __future__ import annotations
import time
import pathlib

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

import ezdxf
import ezdxf.path
from ezdxf.math import Matrix44
from ezdxf.tools.font_manager import FontManager, FontNotFoundError
from ezdxf.tools.ttfonts import TTFontRenderer

font_manager = FontManager()


def make_example(doc, font_name: str, y: float, text: str, kerning: bool):
    try:
        font = font_manager.get_ttf_font(font_name)
        font_renderer = TTFontRenderer(font, kerning=kerning)
    except FontNotFoundError:
        return
    style = f"STYLE{y}"
    doc.styles.add(style, font=font_name)
    msp = doc.modelspace()
    cap_height = 100
    measurements = font_renderer.font_measurements
    x_height = measurements.x_height * font_renderer.get_scaling_factor(cap_height)

    s = f"{font_renderer.font_name}: {text}"
    text_path = font_renderer.get_text_path(s, cap_height=cap_height)
    length = font_renderer.get_text_length(s, cap_height=cap_height)
    msp.add_line((0, y), (length, y), dxfattribs={"color": 3})
    msp.add_line((0, y + cap_height), (length, y + cap_height), dxfattribs={"color": 3})
    msp.add_line((0, y + x_height), (length, y + x_height), dxfattribs={"color": 5})
    msp.add_text(
        s, height=cap_height, dxfattribs={"color": 6, "layer": "TEXT", "style": style}
    ).set_placement((0, y))
    ezdxf.path.render_hatches(
        msp,
        [text_path.transform(Matrix44.translate(0, y, 0))],
        dxfattribs={"color": 7, "layer": "HATCH"},
    )


FONTS = [
    "simsun.ttc",
    "arial.ttf",
    "arialn.ttf",
    "ariblk.ttf",
    "isocpeur.ttf",
    "LiberationSans-Regular.ttf",
    "LiberationSerif-Regular.ttf",
    "LiberationSansNarrow-Regular.ttf",
    "LiberationMono-Regular.ttf",
    "OpenSans-Regular.ttf",
    "OpenSansCondensed-Light.ttf",
    "DejavuSerif.ttf",
    "DejavuSerifCondensed.ttf",
    "DejavuSans.ttf",
    "DejavuSansCondensed.ttf",
]


def latin():
    doc = ezdxf.new()
    doc.layers.add("TEXT")
    doc.layers.add("HATCH").off()

    y = 0
    for font in FONTS:
        print(f"render font: {font}")
        make_example(
            doc,
            font,
            y,
            text="AXxpEHIäüöÄÜÖß%& VA LW T. TA Ts ... and much more text  !!!!!!",
            kerning=False,
        )
        y += 150
    doc.saveas(CWD / "latin_glyphs.dxf")


def chinese():
    doc = ezdxf.new()
    doc.layers.add("TEXT")
    doc.layers.add("HATCH").off()

    y = 0
    for font in FONTS:
        print(f"render font: {font}")
        make_example(
            doc,
            font,
            y,
            text="AXxp 向中国问好 向中国问好 向中国问好 !!!!!!",
            kerning=False,
        )
        y += 150
    doc.saveas(CWD / "chinese_glyphs.dxf")


def cache_reloading():
    t0 = time.perf_counter()
    cache_file = pathlib.Path("font_cache.json")
    if cache_file.exists():
        with open(cache_file, "rt") as fp:
            font_manager.loads(fp.read())
        print(f"loaded cache in {time.perf_counter() - t0:.4f} seconds")
    else:
        print(f"build cache file: {cache_file.name}")
        font_manager.build()
        print(f"build cache in {time.perf_counter() - t0:.4f} seconds")
        s = font_manager.dumps()
        print(f"writing cache file: {cache_file.name}")
        with open("font_cache.json", "wt") as fp:
            fp.write(s)


if __name__ == "__main__":
    cache_reloading()
    latin()
    chinese()
