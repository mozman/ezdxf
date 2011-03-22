#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: System Default Table
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import logging

class SystemTable:
    """ Store some required system values, mostly only required for AutoCAD.

    Use the first DICTIONARY in the OBJECTS-SECTION
    """
    def __init__(self, drawing):
        self._values = dict()
        self._drawing = drawing
        self._setup()
        del self._drawing

    def __getitem__(self, key):
        return self._values[key]

    def _setup(self):
        self._values['DefaultPlotStyleHandle'] = self._get_default_plot_style_handle()

    def _get_default_plot_style_handle(self):
        handle = None
        try:
            layer0 = self._drawing.layers.get('0')
        except AttributeError:
            logging.warning("layer table is not present.")
        except ValueError:
            logging.warning("layer '0' is not present.")
        else:
            try:
                handle = layer0.tags.getvalue(390)
            except ValueError:
                logging.warning("required Default Plot Style Handle is not present.")
        return handle
