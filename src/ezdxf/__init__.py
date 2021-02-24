# Copyright (C) 2011-2020, Manfred Moitzi
# License: MIT License
import sys
import os
from .version import version, __version__

VERSION = __version__
__author__ = "mozman <me@mozman.at>"

TRUE_STATE = {'True', 'true', 'On', 'on', '1'}
PYPY = hasattr(sys, 'pypy_version_info')
PYPY_ON_WINDOWS = sys.platform.startswith('win') and PYPY
EZDXF_TEST_FILES = os.getenv('EZDXF_TEST_FILES', '')

# Set EZDXF_AUTO_LOAD_FONTS to "False" to deactivate auto font loading,
# if this this procedure slows down your startup time and font measuring is not
# important to you. Fonts can always loaded manually: ezdxf.fonts.load()
EZDXF_AUTO_LOAD_FONTS = os.getenv('EZDXF_AUTO_LOAD_FONTS', 'True') in TRUE_STATE

# name space imports - do not remove
from ezdxf.options import options
from ezdxf.colors import (
    int2rgb, rgb2int, transparency2float, float2transparency,
)
from ezdxf.lldxf import const
from ezdxf.lldxf.validator import is_dxf_file, is_dxf_stream
from ezdxf.filemanagement import readzip, new, read, readfile, decode_base64
from ezdxf.tools.standards import (
    setup_linetypes, setup_styles,
    setup_dimstyles, setup_dimstyle,
)
from ezdxf.tools import pattern, fonts
from ezdxf.render.arrows import ARROWS
from ezdxf.lldxf.const import (
    DXFError, DXFStructureError, DXFVersionError, DXFTableEntryError,
    DXFAppDataError, DXFXDataError, DXFAttributeError, DXFValueError,
    DXFKeyError, DXFIndexError, DXFTypeError, DXFBlockInUseError,
    InvalidGeoDataException, InsertUnits,
    ACI, DXF12, DXF2000, DXF2004, DXF2007, DXF2010, DXF2013, DXF2018,
)
# name space imports - do not remove

import codecs
from ezdxf.lldxf.encoding import (
    dxf_backslash_replace, has_dxf_unicode, decode_dxf_unicode,
)

# setup DXF unicode encoder -> '\U+nnnn'
codecs.register_error('dxfreplace', dxf_backslash_replace)

# Load font support automatically:
if EZDXF_AUTO_LOAD_FONTS:
    fonts.load()

YES_NO = {True: 'yes', False: 'no'}


def print_config(func=print, verbose=False):
    from pathlib import Path
    from ezdxf.acc import USE_C_EXT

    func(f"ezdxf v{__version__} @ {Path(__file__).parent}")
    func(f"Python version: {sys.version}")
    func(f"using C-extensions: {YES_NO[USE_C_EXT]}")
    func(f"using Matplotlib: {YES_NO[options.use_matplotlib]}")
    if verbose:
        font_cache_dir = options.font_cache_directory
        if font_cache_dir is False:
            font_cache_dir = 'internal'
        func(f"font cache directory: {font_cache_dir}")
        func(f"default text style: {options.default_text_style}")
        func(f"default dimension text style: "
             f"{options.default_dimension_text_style}")
        func(f"load proxy graphic: {YES_NO[options.load_proxy_graphics]}")
        func(f"store proxy graphic: {YES_NO[options.store_proxy_graphics]}")
        func(f"log unprocessed: {YES_NO[options.log_unprocessed_tags]}")
        func(f"filter invalid XDATA group codes: "
             f"{YES_NO[options.filter_invalid_xdata_group_codes]}")
        for v in options.CONFIG_VARS:
            func(f"{v}={os.environ.get(v, '')}")
