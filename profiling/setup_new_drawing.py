# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from timeit import Timer
import ezdxf

SETUP = """
from __main__ import setup_drawing
"""


def setup_drawing():
    doc = ezdxf.new()
    _ = doc.dxfversion


def main(count):
    t = Timer("setup_drawing()", SETUP)
    time2 = t.timeit(count)
    print_result(time2, f"setup {count} new style DXF")


def print_result(time, text):
    print(f"Profiling: {text}; takes {time:.2f} seconds")


if __name__ == "__main__":
    main(300)
