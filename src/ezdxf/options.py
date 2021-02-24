# Copyright (c) 2011-2021, Manfred Moitzi
# License: MIT License
import os

# The MATPLOTLIB global shows that Matplotlib is installed:
try:
    import matplotlib

    MATPLOTLIB = True
except ImportError:
    MATPLOTLIB = False

TRUE_STATE = {'True', 'true', 'On', 'on', '1'}
EZDXF_FONT_CACHE_DIRECTORY = os.getenv(
    'EZDXF_FONT_CACHE_DIRECTORY', False)
EZDXF_PRESERVE_PROXY_GRAPHICS = os.getenv(
    'EZDXF_PRESERVE_PROXY_GRAPHICS', 'True') in TRUE_STATE
EZDXF_LOG_UNPROCESSED_TAGS = os.getenv(
    'EZDXF_LOG_UNPROCESSED_TAGS', 'True') in TRUE_STATE
EZDXF_FILTER_INVALID_XDATA_GROUP_CODES = os.getenv(
    'EZDXF_FILTER_INVALID_XDATA_GROUP_CODES', 'False') in TRUE_STATE


class Options:
    CONFIG_VARS = [
        "EZDXF_DISABLE_C_EXT",
        "EZDXF_TEST_FILES",
        "EZDXF_FONT_CACHE_DIRECTORY",
        "EZDXF_AUTO_LOAD_FONTS",
        "EZDXF_PRESERVE_PROXY_GRAPHICS",
        "EZDXF_LOG_UNPROCESSED_TAGS",
        "EZDXF_FILTER_INVALID_XDATA_GROUP_CODES",
    ]

    def __init__(self):
        self.filter_invalid_xdata_group_codes = EZDXF_FILTER_INVALID_XDATA_GROUP_CODES
        self.default_text_style = 'OpenSans'
        self.default_dimension_text_style = 'OpenSansCondensed-Light'

        # Set path to an external font cache directory: e.g. "~/ezdxf", see
        # docs for ezdxf.options for an example how to create your own
        # external font cache:
        self.font_cache_directory = EZDXF_FONT_CACHE_DIRECTORY

        # debugging
        self.log_unprocessed_tags = EZDXF_LOG_UNPROCESSED_TAGS

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

    def preserve_proxy_graphics(self, state=True):
        """ Enable/disable proxy graphic load/store support. """
        self.load_proxy_graphics = state
        self.store_proxy_graphics = state


# Global Options
options = Options()

if EZDXF_PRESERVE_PROXY_GRAPHICS:
    options.preserve_proxy_graphics(True)
else:
    options.preserve_proxy_graphics(False)