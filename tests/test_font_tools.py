# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import sys
import ezdxf
from ezdxf.tools.fonts import font


def test_font_arial():
    f = font('arial.ttf')
    assert f.font.name == 'arial.ttf'

    g = font('arial.ttf')
    # has to return the same object, double initialization of font by tkinter not supported
    assert f is g


def test_get_font_tool():
    dwg = ezdxf.new('R12', setup=True)
    style = dwg.styles.get('OPEN_SANS')
    ft = style.tk_font_tool()
    assert ft.font.name == 'OpenSans-Regular.ttf'

    # is tk running
    if sys.platform.startswith('win'):
        # PyPy3 has no integrated Tcl 8.3
        if hasattr(sys, 'pypy_version_info'):
            assert ft.Tk is False, 'Tk initialisation seems to work now!'
