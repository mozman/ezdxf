# Purpose: options module
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"


class Options(object):
    def __init__(self):
        self.template_dir = None

        # compress tags of unknown chunks of tags like unknown sections
        self.compress_default_chunks = False

        # compress binary data tags 310-319, collects multiple succeeding binary tags as one compressed tag
        self.compress_binary_data = False
        self.store_comments = True

# Global Options
options = Options()
