# Created: 10.03.2011
# Copyright (C) 2011-2020, Manfred Moitzi
# License: MIT License
import sys
from .version import version, __version__

VERSION = __version__
__author__ = "mozman <me@mozman.at>"

PYPY = hasattr(sys, 'pypy_version_info')
PYPY_ON_WINDOWS = sys.platform.startswith('win') and PYPY

# name space imports - do not remove
from ezdxf.options import options
from ezdxf.tools import transparency2float, float2transparency
from ezdxf.tools.rgb import int2rgb, rgb2int
from ezdxf.lldxf import const
from ezdxf.lldxf.validator import is_dxf_file, is_dxf_stream
from ezdxf.filemanagement import readzip, new, read, readfile, decode_base64
from ezdxf.tools.standards import (
    setup_linetypes, setup_styles,
    setup_dimstyles, setup_dimstyle,
)
from ezdxf.tools import pattern
from ezdxf.render.arrows import ARROWS
from ezdxf.lldxf.const import (
    DXFError, DXFStructureError, DXFVersionError, DXFTableEntryError,
    DXFAppDataError, DXFXDataError, DXFAttributeError, DXFValueError,
    DXFKeyError, DXFIndexError, DXFTypeError, DXFBlockInUseError, InsertUnits,
    ACI, DXF12, DXF2000, DXF2004, DXF2007, DXF2010, DXF2013, DXF2018,
)
# name space imports - do not remove

import codecs
from ezdxf.lldxf.encoding import dxf_backslash_replace

# setup DXF unicode encoder -> '\U+nnnn'
codecs.register_error('dxfreplace', dxf_backslash_replace)
