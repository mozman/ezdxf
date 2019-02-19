# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from timeit import Timer
import ezdxf

SETUP = """
from __main__ import setup_old_style_dxf, setup_new_style_dxf
"""


def setup_old_style_dxf():
    doc = ezdxf.new('R2018')
    _ = doc.dxfversion


def setup_new_style_dxf():
    doc = ezdxf.new2()
    _ = doc.dxfversion


def main(count):
    t = Timer("setup_old_style_dxf()", SETUP)
    time1 = t.timeit(count)
    print_result(time1, 'setup {} old style DXF'.format(count))

    t = Timer("setup_new_style_dxf()", SETUP)
    time2 = t.timeit(count)
    print_result(time2, 'setup {} new style DXF'.format(count))

    print("Ratio old/new: {:.2f}:1".format(time1/time2))


def print_result(time, text):
    print("Profiling: {}; takes {:.2f} seconds".format(text, time))


if __name__ == '__main__':
    main(300)
