# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import sys
import ezdxf
from ezdxf.tools.fonts import font


def test_font_OpenSans():
    f = font('OpenSans-Regular.ttf')
    assert f.font.name == 'OpenSans-Regular.ttf'

    g = font('OpenSans-Regular.ttf')
    # has to return the same object, double initialization of font by tkinter not supported
    assert f is g


def test_unavilable_font():
    f = font('MozManDoNotExist.ttf')
    assert f.font.name == 'MozManDoNotExist.ttf'


def test_get_font_tool():
    dwg = ezdxf.new('R12', setup=True)
    style = dwg.styles.get('OpenSans')
    ft = style.tk_font_tool()
    assert ft.font.name == 'OpenSans-Regular.ttf'

    # is tk running
    if sys.platform.startswith('win'):
        # PyPy3 has no integrated Tcl 8.3
        if hasattr(sys, 'pypy_version_info'):
            assert ft.Tk is False, 'Tk initialisation seems to work now!'
