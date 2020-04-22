# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Dict, List, Tuple
import struct

from ezdxf.tools.binarydata import BitStream
from .const import *
from .crc import crc8
from .fileheader import FileHeader

TYPE_TO_DXF_NAME = {
    0x01: 'TEXT',
    0x02: 'ATTRIB',
    0x03: 'ATTDEF',
    0x04: 'BLOCK',
    0x05: 'ENDBLK',
    0x06: 'SEQEND',
    0x07: 'INSERT',
    0x08: 'MINSERT',
    0x0A: 'VERTEX_2D',
    0x0B: 'VERTEX_3D',
    0x0C: 'VERTEX_MESH',
    0x0D: 'VERTEX_PFACE',
    0x0E: 'VERTEX_PFACE_FACE',
    0x0F: 'POLYLINE_2D',
    0x10: 'POLYLINE_3D',
    0x11: 'ARC',
    0x12: 'CIRCLE',
    0x13: 'LINE',
    0x14: 'DIMENSION_ORDINATE',
    0x15: 'DIMENSION_LINEAR',
    0x16: 'DIMENSION_ALIGNED',
    0x17: 'DIMENSION_ANG_3PT',
    0x18: 'DIMENSION_ANG_2LN',
    0x19: 'DIMENSION_RADIUS',
    0x1A: 'DIMENSION_DIAMETER',
    0x1B: 'POINT',
    0x1C: '3DFACE',
    0x1D: 'POLYLINE_PFACE',
    0x1E: 'POLYLINE_MESH',
    0x1F: 'SOLID',
    0x20: 'TRACE',
    0x21: 'SHAPE',
    0x22: 'VIEWPORT',
    0x23: 'ELLIPSE',
    0x24: 'SPLINE',
    0x25: 'REGION',
    0x26: '3DSOLID',
    0x27: 'BODY',
    0x28: 'RAY',
    0x29: 'XLINE',
    0x2A: 'DICTIONARY',
    0x2B: 'OLEFRAME',
    0x2C: 'MTEXT',
    0x2D: 'LEADER',
    0x2E: 'TOLERANCE',
    0x2F: 'MLINE',
    0x30: 'BLOCK_RECORD_CTRL_OBJ',
    0x31: 'BLOCK_RECORD',
    0x32: 'LAYER_CTRL_OBJ',
    0x33: 'LAYER',
    0x34: 'STYLE_CTRL_OBJ',
    0x35: 'STYLE',
    0x38: 'LTYPE_CTRL_OBJ',
    0x39: 'LTYPE',
    0x3C: 'VIEW_CTRL_OBJ',
    0x3D: 'VIEW',
    0x3E: 'UCS_CTRL_OBJ',
    0x3F: 'UCS',
    0x40: 'VPORT_CTRL_OBJ',
    0x41: 'VPORT',
    0x42: 'APPID_CTRL_OBJ',
    0x43: 'APPID',
    0x44: 'DIMSTYLE_CTRL_OBJ',
    0x45: 'DIMSTYLE',
    0x46: 'VIEWPORT_ENTITY_HDR_CTRL_OBJ',
    0x47: 'VIEWPORT_ENTITY_HDR',
    0x48: 'GROUP',
    0x49: 'MLINESTYLE',
    0x4A: 'OLE2FRAME',
    0x4C: 'LONG_TRANSACTION',
    0x4D: 'LWPOLYLINE',
    0x4E: 'HATCH',
    0x4F: 'XRECORD',
    0x50: 'ACDBPLACEHOLDER',
    0x51: 'VBA_PROJECT',
    0x52: 'LAYOUT',
    0x1F2: 'ACAD_PROXY_ENTITY',
    0x1F3: 'ACAD_PROXY_OBJECT',
}


# Objects with non-fixed values:
# object type to DXF name mapping: DwgDocument.dxf_object_types[...]
# ACAD_TABLE
# CELLSTYLEMAP
# DBCOLOR
# DICTIONARYVAR
# DICTIONARYWDFLT
# FIELD
# GROUP >> 0x48
# HATCH >> 0x4E
# IDBUFFER
# IMAGE
# IMAGEDEF
# IMAGEDEFREACTOR
# LAYER_INDEX
# LAYOUT >> 0x52
# LWPLINE >> 0x4D
# MATERIAL
# MLEADER
# MLEADERSTYLE
# OLE2FRAME  >> 0x4A
# PLACEHOLDER
# PLOTSETTINGS
# RASTERVARIABLES
# SCALE
# SORTENTSTABLE
# SPATIAL_FILTER
# SPATIAL_INDEX
# TABLEGEOMETRY
# TABLESTYLES
# VBA_PROJECT >> 0x51
# VISUALSTYLE
# WIPEOUTVARIABLE
# XRECORD >> 0x4F

class DwgObject:
    def __init__(self, specs: FileHeader, data: Bytes, handle: str = ''):
        self.specs = specs
        # data start after the leading size value as modular shorts or modular chars
        self.data: Bytes = data
        self.dxfname: str = ''
        self.handle: str = handle
        self.owner: str = ''
        self.object_type: int = 0  # 0 == unused!
        self.object_common_data_location = 0  # start location of common object data in bits
        self.object_data_size: int = 0  # object data size in bits or 'endbit' of pre-handles section
        self.object_data_location: int = 0  # start location of object specific data in bits
        self.persistent_reactors_count: int = 0
        self.persistent_reactors: List[str] = []  # list of handles as hex string
        self.has_xdictionary = False
        self.xdictionary: str = ''  # handle to XDictionary as hex string
        self.has_data_store_content = False
        self.handle_stream_size: int = 0  # size in bits
        self.object_handles_location: int = 0  # start location of object specific handles in bits
        self.load_common_data()
        self.load_common_handles()

    @property
    def version(self):
        return self.specs.version

    @property
    def encoding(self):
        return self.specs.encoding

    def load_common_data(self) -> None:
        version = self.version
        bs = BitStream(self.data, version, self.encoding)
        if version >= ACAD_2010:
            self.handle_stream_size = bs.read_unsigned_modular_chars()
        self.object_type = bs.read_object_type()

        if ACAD_2000 <= version <= ACAD_2007:
            self.object_data_size = bs.read_unsigned_long()
        handle = bs.read_hex_handle()
        if handle != self.handle:
            raise DwgObjectError(
                f'Handle stored inside of object (#{handle}) does not match handle in objects map (#{self.handle}).')
        extended_data_size = bs.read_bit_short()
        if extended_data_size > 0:
            # todo: implement extended data loader
            bs.skip(extended_data_size * 8)
        if ACAD_13 <= version <= ACAD_14:
            self.object_data_size = bs.read_unsigned_long()
        # common?
        self.persistent_reactors_count = bs.read_bit_long()
        if version >= ACAD_2004:
            self.has_xdictionary = bool(bs.read_bit())
        if version >= ACAD_2013:
            self.has_data_store_content = bool(bs.read_bit())
        self.object_data_location = bs.bit_index

    def init_handle_stream(self) -> BitStream:
        bs = BitStream(self.data, self.specs.version)
        bs.bit_index = self.object_data_location + self.object_data_size
        return bs

    def load_common_handles(self) -> None:
        bs = self.init_handle_stream()
        self.owner = bs.read_handle()
        self.persistent_reactors.extend(bs.read_hex_handle() for _ in range(self.persistent_reactors_count))
        if self.has_xdictionary:
            self.xdictionary = bs.read_hex_handle()
        self.object_handles_location = bs.bit_index

    def update_dxfname(self, dxf_object_types: Dict[int, str]) -> None:
        object_type = self.object_type
        if object_type < 500:
            dxfname = TYPE_TO_DXF_NAME.get(object_type)
        else:
            dxfname = dxf_object_types.get(object_type)

        if dxfname:
            self.dxfname = dxfname
        else:
            raise DwgObjectError(f'Invalid/unknown object type: {object_type}.')


def dwg_object_data_size(data: Bytes, location: int, version: str) -> Tuple[int, int]:
    bs = BitStream(data[location: location + 4])
    if version >= ACAD_2010:
        object_size = bs.read_unsigned_modular_chars()
    else:
        object_size = bs.read_modular_shorts()
    size_size = bs.bit_index >> 3
    return location + size_size, object_size


class Directory:
    def __init__(self):
        self.objects: Dict[str, DwgObject] = dict()

    def add(self, obj: DwgObject) -> None:
        self.objects[obj.handle] = obj

    def __getitem__(self, handle: str) -> DwgObject:
        return self.objects[handle]

    def __contains__(self, handle: str) -> bool:
        return handle in self.objects

    def load(self, specs: FileHeader, data: Bytes, object_map: Dict[str, int], crc_check=False) -> None:
        version = specs.version
        for handle, location in object_map.items():
            object_start, object_size = dwg_object_data_size(data, location, version)
            object_end = object_start + object_size
            object_data = data[object_start: object_end]
            if crc_check:
                check = struct.unpack_from('<H', data, object_end)
                crc = crc8(object_data, seed=0xc0c1)
                if check != crc:
                    raise CRCError(f'CRC error in object #{handle}.')
            self.add(DwgObject(specs, object_data, handle))
