# Created: 01.01.2019: font measuring by tkinter
# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from tkinter import Tk, TclError
from tkinter.font import Font as TkFont


class FakeTkFont:
    def __init__(self, name):
        self.name = name

    def measure(self, s: str):
        return len(s)


class Font:
    fonts = {}
    Tk = None
    SIZE = 100

    def __init__(self, name: str):
        if Font.Tk is None:
            try:
                Font.Tk = Tk()  # initialization of Tk is necessary
            except TclError:  # PyPy3 has no integrated Tcl 8.3 on Windows and did not found a proper installation of Tcl either
                Font.Tk = False
        if Font.Tk:
            self.font = TkFont(name=name, size=self.SIZE)
        else:
            self.font = FakeTkFont(name)

    def measure(self, s: str):
        """ Normalized measurement. """
        return float(self.font.measure(s)) / float(self.SIZE)

    def str_width(self, s: str, height=1., ratio=1.) -> float:
        """ Measurement scaled to text height and height/width ratio."""
        return self.measure(s) * height * ratio

    def text_width(self, text_entity) -> float:
        """
        Measurement scaled to text height and height/width ratio. Getting all data from TEXT entity.

        """
        s = text_entity.get_dxf_attrib('text',  '')
        height = text_entity.get_dxf_attrib('height',  1.0)
        style_name = text_entity.get_dxf_attrib('style',  'STANDARD')
        style = text_entity.drawing.styles.get(style_name)
        width = style.get_dxf_attrib('width', 1.0)
        return self.str_width(s, height=height, ratio=width)


def font(name):
    try:
        return Font.fonts[name]
    except KeyError:
        Font.fonts[name] = Font(name)
    return Font.fonts[name]
