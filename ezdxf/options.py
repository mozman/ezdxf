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
        self._debug = False
        self.template_dir = None
        self.logger = logging.getLogger(LOGGER_NAME)
        self.debug = False  # important to set after setup of self.logger

        # compress tags of unknown chunks of tags like unknown sections
        self.compress_default_chunks = False

        # compress binary data tags 310-319, collects multiple succeeding binary tags as one compressed tag
        self.compress_binary_data = False

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