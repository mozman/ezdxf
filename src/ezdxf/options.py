# Copyright (c) 2011-2021, Manfred Moitzi
# License: MIT License

# The MATPLOTLIB global shows that Matplotlib is installed:
try:
    import matplotlib
    MATPLOTLIB = True
except ImportError:
    MATPLOTLIB = False


class Options:
    def __init__(self):
        self.filter_invalid_xdata_group_codes = False
        self.default_text_style = 'OpenSans'
        self.default_dimension_text_style = 'OpenSansCondensed-Light'

        # Set path to an external font cache directory: e.g. "~/ezdxf", see
        # docs for ezdxf.options for an example how to create your own
        # external font cache:
        self.font_cache_directory = False

        # debugging
        self.log_unprocessed_tags = True

        # Proxy graphic handling:
        # Set 'load_proxy_graphics' to True for loading proxy graphics
        self.load_proxy_graphics = False
        # Set 'store_proxy_graphics' to True for exporting proxy graphics
        self.store_proxy_graphics = False

        # Enable this option to always create same meta data for testing
        # scenarios, e.g. to use a diff like tool to compare DXF documents.
        self.write_fixed_meta_data_for_testing = False

        # Activate/deactivate Matplotlib support (e.g. for testing)
        self._use_matplotlib = MATPLOTLIB

    @property
    def use_matplotlib(self) -> bool:
        """ Activate/deactivate Matplotlib support e.g. for testing """
        return self._use_matplotlib

    @use_matplotlib.setter
    def use_matplotlib(self, state: bool):
        if MATPLOTLIB:
            self._use_matplotlib = state
        else:  # Matplotlib is not installed
            self._use_matplotlib = False

    def preserve_proxy_graphics(self):
        """ Enable proxy graphic load/store support. """
        self.load_proxy_graphics = True
        self.store_proxy_graphics = True


# Global Options
options = Options()
