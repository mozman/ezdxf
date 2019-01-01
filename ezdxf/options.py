# Purpose: options module
# Created: 11.03.2011
# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License


class Options:
    def __init__(self):
        self.template_dir = None  # type: str

        # check app data and xdata tag structures, turn this option off for a little performance boost
        self.check_entity_tag_structures = True

        self.default_text_style = 'OPEN_SANS'
        self.default_dimension_text_style = 'OPEN_SANS_CONDENSED_LIGHT'


# Global Options
options = Options()
