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
    print_result(time2, 'setup {} new style DXF'.format(count))


def print_result(time, text):
    print("Profiling: {}; takes {:.2f} seconds".format(text, time))


if __name__ == '__main__':
    main(300)
