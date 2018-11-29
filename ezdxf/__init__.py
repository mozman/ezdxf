# Created: 10.03.2011
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
# name space imports - do not remove
from ezdxf.options import options  # example: ezdxf.options.template_dir = 'c:\templates'
from ezdxf.tools.importer import Importer
from ezdxf.tools import transparency2float, float2transparency  # convert transparency integer values to floats 0..1
from ezdxf.tools.rgb import int2rgb, rgb2int
from ezdxf.tools.pattern import PATTERN
from ezdxf.lldxf import const  # restore module structure ezdxf.const
from ezdxf.lldxf.validator import is_dxf_file, is_dxf_stream
from ezdxf.filemanagement import new, read, readfile, readzip
from ezdxf.tools.standards import setup_linetypes, setup_styles
from ezdxf.lldxf.const import DXFError  # base error exception
from ezdxf.lldxf.const import DXFStructureError, DXFVersionError, DXFTableEntryError, DXFAppDataError, DXFXDataError
from ezdxf.lldxf.const import DXFAttributeError, DXFValueError, DXFKeyError, DXFIndexError, DXFTypeError, DXFInvalidLayerName
from ezdxf.lldxf.const import DXFBlockInUseError
# name space imports - do not remove

import codecs
from ezdxf.lldxf.encoding import dxfbackslashreplace
codecs.register_error('dxfreplace', dxfbackslashreplace)  # setup DXF unicode encoder -> '\U+nnnn'

# 2018-11-29: future consistent version numbers
# ---------------------------------------------
#
# version scheme for __version__: (major, minor, micro, release_level)
#
# major:
#   0 .. not all planned features done
#   1 .. all features available
#   2 .. if significant API change (2, 3, ...)
#
# minor:
#   changes with new features or minor API changes
#
# micro:
#   changes with bug fixes, maybe also minor changes
#
# release_state:
#   a .. alpha: adding new features - non public development state
#   b .. beta: testing new features - public development state
#   rc .. release candidate: testing release - public testing
#   release: public release
# examples
#
# major pre release alpha 2: VERSION = "0.9a2"; __version__ = (0, 9, 0, 'a2')
# major release candidate 0: VERSION = "0.9rc0"; __version__ = (0, 9, 0, 'rc0')
# major release: VERSION = "0.9"; __version__ = (0, 9, 0, 'release')
# 1. bug fix release beta0: VERSION = "0.9.1b0"; __version__ = (0, 9, 1, 'b0')
# 2. bug fix release: VERSION = "0.9.2"; __version__ = (0, 9, 2, 'release')

version = (0, 9, 0, 'a1')  # also update VERSION in setup.py
VERSION = "0.9a1"
__version__ = VERSION
__author__ = "mozman <me@mozman.at>"
