# Purpose: options module
# Created: 11.03.2011
# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License


class Options:
    def __init__(self):
        # check app data and xdata tag structures, turn this option off for a little performance boost
        self.check_entity_tag_structures = True
        self.filter_invalid_xdata_group_codes = False

        self.default_text_style = 'OpenSans'
        self.default_dimension_text_style = 'OpenSansCondensed-Light'

        # debugging
        self.log_unprocessed_tags = True


# Global Options
options = Options()
