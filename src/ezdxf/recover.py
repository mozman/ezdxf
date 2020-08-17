#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from typing import TYPE_CHECKING, BinaryIO

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing

# TODO: recover
#  Mimic the CAD "RECOVER" command, try to read messy DXF files,
#  needs only as much work until the regular ezdxf loader can handle
#  and audit the DXF file:
#
# - recover missing ENDSEC and EOF tags
# - merge multiple sections with same name
# - reorder sections
# - merge multiple tables with same name
# - apply repair layers to replace legacy_mode from read/readfile:
#       - repair.fix_coordinate_order()
#       - repair.tag_reorder_layer
#       - repair.filter_invalid_yz_point_codes
# - recover tags "outside" of sections
# - move header variable tags (9, "$...") into HEADER section


def read(stream: BinaryIO) -> 'Drawing':
    """ Read a DXF document from a binary-stream similar to :func:`ezdxf.read`,
    But this function will detect the text encoding automatically and repair
    as much flaws as possible to take the document to a state, where the
    :class:`~ezdxf.audit.Auditor` could start his journey to repair further issues.

    Args:
        stream: data stream to load in binary read mode

    """
    pass


def readfile(filename: str) -> 'Drawing':
    """ Read a DXF document from file system similar to :func:`ezdxf.readfile`,
    but this function will repair as much flaws as possible to take the document
    to a state, where the :class:`~ezdxf.audit.Auditor` could start his journey
    to repair further issues.

    Args:
        filename: file-system name of the DXF document to load

    """
    pass
