#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
# API to the ezdxf._acis package
"""
The main goals of these ACIS support libraries are:

    1. load and parse simple and known ACIS data structures
    2. create and export simple and known ACIS data structures

It is NOT a goal to edit and export arbitrary existing ACIS structures.

    Don't even try it!

This modules do not implement an ACIS kernel!!!
So tasks beyond stiching some flat polygonal faces to a polyhedron or creating
simple curves is not possible.

To all beginners: GO AWAY!

"""
from ezdxf._acis.const import (
    AcisException,
    ParsingError,
    InvalidLinkStructure,
    ExportError,
    Tags,
)
from ezdxf._acis.hdr import AcisHeader
from ezdxf._acis.sat import (
    parse_sat,
    SatBuilder,
    SatEntity
)
from ezdxf._acis.sab import (
    parse_sab,
    SabBuilder,
    SabEntity
)
from ezdxf._acis.abstract import AbstractEntity
from ezdxf._acis import sat
from ezdxf._acis import parsing
from ezdxf._acis import sab
from ezdxf._acis.converter import body_to_mesh
from ezdxf._acis.entities import load