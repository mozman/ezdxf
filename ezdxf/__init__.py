# Created: 10.03.2011
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
# import version data
from .version import version, __version__
VERSION = __version__
__author__ = "mozman <me@mozman.at>"

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

