# Purpose: options module
# Created: 11.03.2011
# Copyright (c) 2011-2012, Manfred Moitzi
# License: MIT License


class Options:
    def __init__(self):
        # check app data and xdata tag structures, turn this option off for a little performance boost
        self.check_entity_tag_structures = True
        self.filter_invalid_xdata_group_codes = False
        self.default_text_style = 'OpenSans'
        self.default_dimension_text_style = 'OpenSansCondensed-Light'

        # Predefined hatch pattern in ezdxf before v0.11 were scaled too small, by a factor of 1/25.4, compared with
        # the predefined pattern in BricsCAD and AutoCAD, this was corrected in v0.11, but if your application
        # depends on the old scaling and changing your code is too much work, set 'use_old_predefined_pattern_scaling'
        # option to True to use the old pattern scaling.
        self.use_old_predefined_pattern_scaling = False
        # debugging
        self.log_unprocessed_tags = True

        # Proxy graphic handling:
        # Set 'load_proxy_graphics' to True for loading proxy graphics
        self.load_proxy_graphics = False
        # Set 'store_proxy_graphics' to True for exporting proxy graphics
        self.store_proxy_graphics = False

        # Enable this option to always create same meta data for testing scenarios, e.g. to use a diff like tool to
        # compare DXF documents.
        self.write_fixed_meta_data_for_testing = False

    def preserve_proxy_graphics(self):
        """ Enable proxy graphic load/store support. """
        self.load_proxy_graphics = True
        self.store_proxy_graphics = True


# Global Options
options = Options()
