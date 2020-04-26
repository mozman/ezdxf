# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Dict, List, Tuple, Optional, Any
import struct
from abc import abstractmethod

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


class DwgRootObject:
    """ Common super class for DwgObject() and DwgEntity(). """

    def __init__(self, specs: FileHeader, data: Bytes, handle: str = ''):
        self.specs = specs
        # data start after the leading size value as modular shorts or modular chars
        self.data: Bytes = data
        self.dxfname: str = ''
        self.dxfattribs: Dict[str, Any] = dict()
        self.dxfattribs['handle'] = handle
        self.persistent_reactors_count: int = 0
        self.persistent_reactors: List[str] = []  # list of handles as hex string
        self.has_xdictionary = False
        self.xdictionary: str = ''  # handle to XDictionary as hex string
        self.has_data_store_content = False

        # set by init_data_stream():
        self.handle_stream_size: int = 0  # size in bits, required for later usage?
        self.object_data_start: int = 0  # start of object data - first bit of object type
        self.data_stream = self.init_data_stream()

        # set by load_common_data():
        self.object_type: int = 0  # 0 == unused!
        self.object_data_size: int = 0
        self.load_common_data()

        # R13+: All handles are stored in the handle stream
        self.handle_stream: BitStream = self.init_handle_stream()

        # R2007+: All Strings are stored in the string stream
        self.string_stream: Optional[BitStream] = self.init_string_stream()

        # Data loading process:
        self.load_data()

    @property
    def version(self):
        return self.specs.version

    @property
    def encoding(self):
        return self.specs.encoding

    @property
    def handle(self) -> str:
        return self.dxfattribs['handle']

    @property
    def handle_section_start(self) -> int:
        return self.object_data_start + self.object_data_size

    def init_data_stream(self) -> BitStream:
        version = self.version
        bs = BitStream(self.data, version, self.encoding)
        if version >= ACAD_2010:
            self.handle_stream_size = bs.read_unsigned_modular_chars()
        self.object_data_start = bs.bit_index
        return bs

    def load_common_data(self) -> None:
        version = self.version
        bs = self.data_stream
        bs.reset(self.object_data_start)
        self.object_type = bs.read_object_type()

        # Read objects data size for R2000+
        if ACAD_2000 <= version <= ACAD_2007:
            # object data size in bits or 'endbit' of pre-handles section
            # start is first bit of object type?
            self.object_data_size = bs.read_unsigned_long()
        elif version >= ACAD_2010:
            # todo: R2010+ - calculate object size in bits
            pass

        # Read handle and check if equal to objects map entry
        handle = bs.read_hex_handle()
        if handle != self.handle:
            raise DwgObjectError(
                f'Handle stored inside of object (#{handle}) does not match handle in objects map (#{self.handle}).')

        # Entity Extended data
        extended_data_size = bs.read_bit_short()
        if extended_data_size > 0:
            # todo: implement extended data loader
            bs.move(extended_data_size * 8)
        # Here is the data fork of DwgObject and DwgEntity.

    def init_handle_stream(self) -> BitStream:
        bs = BitStream(self.data, self.specs.version)
        bs.reset(self.handle_section_start)
        return bs

    def init_string_stream(self) -> Optional[BitStream]:
        if self.version >= ACAD_2007:
            bs = BitStream(self.data, self.specs.version)
            bs.reset(self.handle_section_start - 1)
            if bs.read_bit():  # string stream present
                # ODA error: string stream size calculation - 16 bytes should be 16 bits
                bs.move(-17)  # 1 bit and 1 short back
                size = bs.read_unsigned_short()  # 1 short forward
                if size & 0x8000:
                    bs.move(-32)  # 2 shorts back
                    hi_size = bs.read_unsigned_short()  # 1 short forward
                    size = (size & 0x7fff) | (hi_size << 15)
                bs.move(-16)  # 1 short back, set index to start of size or hi_size value
                # string stream starts backward from from start location of size or hi_size value
                bs.move(-size)
                return bs
        return None

    def load_data(self) -> None:
        self.load_specific_data()
        self.load_common_handles()
        self.load_specific_handles()

    @abstractmethod
    def load_specific_data(self):
        pass

    def load_common_handles(self) -> BitStream:
        bs = self.handle_stream = self.init_handle_stream()
        self.dxfattribs['owner'] = bs.read_handle()
        self.persistent_reactors.extend(bs.read_hex_handle() for _ in range(self.persistent_reactors_count))
        if self.has_xdictionary:
            self.xdictionary = bs.read_hex_handle()
        return bs

    @abstractmethod
    def load_specific_handles(self):
        pass

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


class DwgObject(DwgRootObject):
    def load_common_data(self) -> None:
        super().load_common_data()
        version = self.version
        # Data stream is located after extended object data (EED in ODS 5.4.1 chapter 20.1)
        bs = self.data_stream
        if version <= ACAD_14:
            self.object_data_size = bs.read_unsigned_long()  # in bits
        # Error in ODS: this entry is present in all DWG version and not R13-R14 only
        self.persistent_reactors_count = bs.read_bit_long()
        if version >= ACAD_2004:
            self.has_xdictionary = not bool(bs.read_bit())
            # todo: how is this flag stored in R2000 and prior?
        if version >= ACAD_2013:
            self.has_data_store_content = bool(bs.read_bit())
        # Specific objects data follow (ODS 5.4.1 chapter 20.1)


class DwgEntity(DwgRootObject):
    def __init__(self, specs: FileHeader, data: Bytes, handle: str = ''):
        self.relative_owner_handle = False
        self.linkers_present = False
        self.linetype_flags: int = 0
        self.plotstyle_flags: int = 0
        self.material_flags: int = 0
        self.has_full_visual_style = False
        self.has_face_visual_style = False
        self.has_edge_visual_style = False
        super().__init__(specs, data, handle)

    def load_common_data(self) -> None:
        super().load_common_data()
        version = self.version
        # Data stream is located after extended object data (EED in ODS 5.4.1 chapter 20.4.1)
        bs = self.data_stream
        dxfattribs = self.dxfattribs

        graphic_image = bs.read_bit()
        if graphic_image:
            if version < ACAD_2010:
                image_size = bs.read_unsigned_long()  # in bytes
            else:
                image_size = bs.read_bit_long_long()  # in bytes
            bs.move(image_size << 3)  # skip graphic

        if version <= ACAD_14:
            self.object_data_size = bs.read_unsigned_long()  # in bits

        self.relative_owner_handle = False
        entity_mode = bs.read_bits(2)
        if entity_mode == 0:
            self.relative_owner_handle = True
        elif entity_mode == 1:
            dxfattribs['paperspace'] = 1
        elif entity_mode == 2:
            dxfattribs['paperspace'] = 0

        self.persistent_reactors_count = bs.read_bit_long(2)

        if version >= ACAD_2004:
            self.has_xdictionary = not bool(bs.read_bit())

        if version >= ACAD_2013:
            self.has_data_store_content = bool(bs.read_bit())

        if version <= ACAD_14:
            self.linetype_flags = 0 if bs.read_bit() else 3

        self.linkers_present = not bool(bs.read_bit())
        if version < ACAD_2004:
            dxfattribs['color'] = bs.read_cm_color()
        else:
            pass  # todo: encoded color

        dxfattribs['ltscale'] = bs.read_bit_double()

        if version >= ACAD_2000:
            self.linetype_flags = bs.read_bits(2)
            self.plotstyle_flags = bs.read_bits(2)

        if version >= ACAD_2007:
            self.material_flags = bs.read_bits(2)
            dxfattribs['shadow_mode'] = bs.read_unsigned_byte()

        if version >= ACAD_2010:
            self.has_full_visual_style = bool(bs.read_bit())
            self.has_face_visual_style = bool(bs.read_bit())
            self.has_edge_visual_style = bool(bs.read_bit())

        dxfattribs['invisible'] = bs.read_bit_short()

        if version >= ACAD_2000:
            dxfattribs['lineweight'] = bs.read_signed_byte()


def dwg_object_data_size(data: Bytes, location: int, version: str) -> Tuple[int, int]:
    bs = BitStream(data[location: location + 4])
    if version >= ACAD_2010:
        object_size = bs.read_unsigned_modular_chars()
    else:
        object_size = bs.read_modular_shorts()
    size_size = bs.bit_index >> 3
    return location + size_size, object_size


def dwg_object_type(data: bytes, version: str) -> int:
    """ Read object type from DWG object data stream, `data` has to start
    after object size (first MS in chapter 20.1).

    """
    bs = BitStream(data, version)
    if version >= ACAD_2010:
        bs.read_unsigned_modular_chars()
    return bs.read_object_type()


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
