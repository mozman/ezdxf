# Copyright (C) 2011-2021, Manfred Moitzi
# License: MIT License
from typing import Callable
import sys
import os
from .version import version, __version__

VERSION = __version__
__author__ = "mozman <me@mozman.at>"

TRUE_STATE = {"True", "true", "On", "on", "1"}
PYPY = hasattr(sys, "pypy_version_info")
PYPY_ON_WINDOWS = sys.platform.startswith("win") and PYPY

# name space imports - do not remove
from ezdxf.options import options, config_files
from ezdxf.colors import (
    int2rgb,
    rgb2int,
    transparency2float,
    float2transparency,
)
from ezdxf.lldxf import const
from ezdxf.lldxf.validator import is_dxf_file, is_dxf_stream
from ezdxf.filemanagement import readzip, new, read, readfile, decode_base64
from ezdxf.tools.standards import (
    setup_linetypes,
    setup_styles,
    setup_dimstyles,
    setup_dimstyle,
)
from ezdxf.tools import pattern, fonts
from ezdxf.render.arrows import ARROWS
from ezdxf.lldxf.const import (
    DXFError,
    DXFStructureError,
    DXFVersionError,
    DXFTableEntryError,
    DXFAppDataError,
    DXFXDataError,
    DXFAttributeError,
    DXFValueError,
    DXFKeyError,
    DXFIndexError,
    DXFTypeError,
    DXFBlockInUseError,
    InvalidGeoDataException,
    InsertUnits,
    ACI,
    DXF12,
    DXF2000,
    DXF2004,
    DXF2007,
    DXF2010,
    DXF2013,
    DXF2018,
)

# name space imports - do not remove

import codecs
from ezdxf.lldxf.encoding import (
    dxf_backslash_replace,
    has_dxf_unicode,
    decode_dxf_unicode,
)

# setup DXF unicode encoder -> '\U+nnnn'
codecs.register_error("dxfreplace", dxf_backslash_replace)

# Load font support automatically:
if options.auto_load_fonts:
    fonts.load()
EZDXF_TEST_FILES = options.test_files

YES_NO = {True: "yes", False: "no"}


def print_config(
    func: Callable[[str], None] = print, verbose: bool = False
) -> None:
    from pathlib import Path
    from ezdxf.acc import USE_C_EXT
    from io import StringIO

    func(f"ezdxf v{__version__} @ {Path(__file__).parent}")
    func(f"Python version: {sys.version}")
    func(f"using C-extensions: {YES_NO[USE_C_EXT]}")
    func(f"using Matplotlib: {YES_NO[options.use_matplotlib]}")
    if verbose:
        func("\nOptions:")
        fp = StringIO()
        options.write(fp)
        for line in fp.getvalue().splitlines():
            func(line)
        func("\nEnvironment Variables:")
        for v in options.CONFIG_VARS:
            func(f"{v}={os.environ.get(v, '')}")

        func("\nExisting Configuration Files:")
        for name in [p for p in config_files() if p.exists()]:
            func(str(name))

