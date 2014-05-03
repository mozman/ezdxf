# Purpose: options module
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

import logging
logging.basicConfig()

LOGGER_NAME = 'ezdxf'


class Options(object):
    def __init__(self):
        self.template_dir = None
        self.logger = logging.getLogger(LOGGER_NAME)
        self.debug = False  # important to set after setup of self.logger
        self.compress_default_chunks = False  # compress tags of unknown chunks of tgas like unknown sections

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value):
        self._debug = bool(value)
        if self._debug:
            self.logger.setLevel('DEBUG')
        else:
            self.logger.setLevel('WARNING')

# Global Options
options = Options()