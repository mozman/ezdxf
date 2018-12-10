# Purpose: options module
# Created: 11.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License


class Options:
    def __init__(self):
        self.template_dir = None  # type: str

        # check app data and xdata tag structures, turn this option off for a little performance boost
        self.check_entity_tag_structures = True


# Global Options
options = Options()
