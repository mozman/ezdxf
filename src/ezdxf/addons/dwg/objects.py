# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Dict, List, Tuple, Optional, Any, TYPE_CHECKING, List
import struct
import logging
from abc import abstractmethod

from ezdxf.tools.binarydata import BitStream
from ezdxf.lldxf.tags import Tags, DXFTag
from .const import *
from .crc import crc8
from .fileheader import FileHeader

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import EntityFactory

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
    0x30: 'BLOCK_RECORD_TABLE',
    0x31: 'BLOCK_RECORD',
    0x32: 'LAYER_TABLE',
    0x33: 'LAYER',
    0x34: 'STYLE_TABLE',
    0x35: 'STYLE',
    0x38: 'LTYPE_TABLE',
    0x39: 'LTYPE',
    0x3C: 'VIEW_TABLE',
    0x3D: 'VIEW',
    0x3E: 'UCS_TABLE',
    0x3F: 'UCS',
    0x40: 'VPORT_TABLE',
    0x41: 'VPORT',
    0x42: 'APPID_TABLE',
    0x43: 'APPID',
    0x44: 'DIMSTYLE_TABLE',
    0x45: 'DIMSTYLE',
    0x46: 'VIEWPORT_ENTITY_TABLE',
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

def dwg_object_data_size(data: Bytes, location: int, version: str) -> Tuple[int, int]:
    """ Returns object start location and object size.

    Args:
        data: raw DWG data
        location: object location from objects map
        version: DWG version string

    """
    bs = BitStream(data[location: location + 4])
    if version >= ACAD_2010:
        object_size = bs.read_unsigned_modular_chars()
    else:
        object_size = bs.read_modular_shorts()
    size_size = bs.bit_index >> 3
    return location + size_size, object_size


def load_table_handles(specs: FileHeader, data: Bytes, handle: str) -> List[str]:
    dwg_object = DwgObject(specs, data, handle)
    num_entries = dwg_object.data_stream.read_bit_long()
    handle = dwg_object.handle_stream.read_hex_handle
    return [handle() for _ in range(num_entries)]


def extended_data_loader(bs: BitStream, size: int, version: str = ACAD_2000) -> List[Tuple]:
    """ Load extended data as list of tuples (group code, value).

    Args:
         bs: data bit stream
         size: size of XDATA to read in bytes
         version: DWG version

    """
    tags = list()
    loaded_data_size = 0
    while loaded_data_size < size:
        code = bs.read_unsigned_byte()
        loaded_data_size += 1
        # code 1 (1001) is invalid - defines appid
        if code == 0:  # string
            if version < ACAD_2007:
                length = bs.read_unsigned_byte()
                codepage = bs.read_unsigned_short()
                encoding = codepage_to_encoding.get(codepage, 'cp1252')
                binary_data = bs.read_bytes(length)
                length += 3
            else:
                length = bs.read_unsigned_short()
                binary_data = bs.read_bytes(length * 2)
                encoding = 'utf16'
                length = (2 + length * 2)
            string = binary_data.decode(encoding=encoding)
            tags.append((1000, string))
            loaded_data_size += length

        elif code == 2:  # structure tag { and }
            char = bs.read_unsigned_byte()
            tags.append((1002, '}' if char else '{'))
            loaded_data_size += 1

        elif code in (3, 5):  # layer table reference or entity handle
            handle = bs.read_unsigned_long_long()
            tags.append((1000 + code, '%X' % handle))
            loaded_data_size += 8

        elif code == 4:  # binary chunk
            length = bs.read_unsigned_byte()
            tags.append((1004, bs.read_bytes(length)))
            loaded_data_size += (length + 1)

        elif code in (40, 41, 42):  # double
            tags.append((1000 + code, bs.read_raw_double()))
            loaded_data_size += 8

        elif code in (10, 11, 12, 13):  # points
            tags.append((1000 + code, bs.read_raw_double(3)))
            loaded_data_size += 24

        elif code == 70:  # short
            tags.append((1070, bs.read_signed_short()))
            loaded_data_size += 2

        elif code == 71:  # long
            tags.append((1071, bs.read_signed_long()))
            loaded_data_size += 4
        else:
            logger.debug(f'DWG Loader: Invalid group code {1000 + code} in XDATA')

    if loaded_data_size != size:
        logger.debug(f'DWG Loader: loaded XDATA size mismatch')

    return tags


class ObjectsDirectory:
    """ A directory of all DWG objects, stored by handle string. """

    def __init__(self):
        self.objects: Dict[str, memoryview] = dict()
        self.locations: Dict[str, int] = dict()

    def __getitem__(self, handle: str) -> memoryview:
        return self.objects[handle]

    def __contains__(self, handle: str) -> bool:
        return handle in self.objects

    def load(self, specs: FileHeader, data: Bytes, object_map: Dict[str, int], crc_check=False) -> None:
        self.locations = object_map
        version = specs.version
        for handle, location in object_map.items():
            object_start, object_size = dwg_object_data_size(data, location, version)
            object_end = object_start + object_size
            object_data = data[object_start: object_end]
            self.objects[handle] = object_data
            crc_check = False  # todo: crc check for objects
            if crc_check:
                check = struct.unpack_from('<H', data, object_end)
                crc = crc8(object_data, seed=0xc0c1)
                if check != crc:
                    raise CRCError(f'CRC error in object #{handle}.')


class DwgRootObject:
    """ Common super class for all DWG objects. """

    def __init__(self, specs: FileHeader, data: Bytes, handle: str = ''):
        self.specs = specs
        # data start after the leading size value as modular shorts or modular chars
        self.data: Bytes = data
        self.dxfname: str = ''
        self.object_type: int = 0  # 0 == unused!
        self.dxfattribs: Dict[str, Any] = dict()
        self.dxfattribs['handle'] = handle
        self.dwg_data: Dict[str, Any] = dict()  # data not used for DXF
        self.persistent_reactors_count: int = 0
        self.persistent_reactors: List[str] = []  # list of handles as hex string
        self.has_xdictionary = False
        self.xdictionary: str = ''  # handle to XDictionary as hex string
        self.xdata: Dict[str, Tags] = dict()
        self.has_data_store_content = False

        # set by init_data_stream():
        self.handle_stream_size: int = 0  # size in bits, required for later usage?
        self.data_stream = self.init_data_stream()

        # set by load_common_data():
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
        return self.object_data_size

    def init_data_stream(self) -> BitStream:
        version = self.version
        bs = BitStream(self.data, version, self.encoding)
        self.object_type = bs.read_object_type()
        if version >= ACAD_2010:
            self.handle_stream_size = bs.read_unsigned_modular_chars()
        return bs

    def load_common_data(self) -> None:
        version = self.version
        bs = self.data_stream

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
        while extended_data_size > 0:
            app_handle = bs.read_hex_handle()
            self.xdata[app_handle] = extended_data_loader(bs, extended_data_size, self.specs.version)
            extended_data_size = bs.read_bit_short()
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
    def load_specific_data(self) -> None:
        pass

    def load_common_handles(self) -> None:
        bs = self.handle_stream
        self.dxfattribs['owner'] = bs.read_handle()
        self.persistent_reactors.extend(bs.read_hex_handle() for _ in range(self.persistent_reactors_count))

        # R13-R2000 the xdictionary handle is always present and is 0 for no xdictionary
        if self.version <= ACAD_2000:
            handle = bs.read_hex_handle()
            if handle != '0':
                self.has_xdictionary = True
                self.xdictionary = handle
        elif self.has_xdictionary:
            self.xdictionary = bs.read_hex_handle()

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

    def dxf(self, factory: 'EntityFactory'):
        entity = factory.new_entity(self.dxfname, self.dxfattribs)
        entity.set_reactors(self.persistent_reactors)

        for handle, tags in self.xdata.items():
            # AppID handles are used as app names and has to be resolved later
            entity.set_xdata(handle, tags)
        return entity


class DwgObject(DwgRootObject):
    """ Base class for non-graphical objects, e.g. LTYPE, LAYER, DICTIONARY, LAYOUT... """

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
            # For <= R2000 xdictionary handle is always present and is 0 for no xdictionary
        # if version >= ACAD_2013: ???
        # self.has_data_store_content = bool(bs.read_bit())
        # Specific objects data follow (ODS 5.4.1 chapter 20.1)


class DwgEntity(DwgRootObject):
    """ Base class for graphical objects, e.g. LINE, CIRCLE, ... """

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


class DwgTableEntry(DwgObject):
    """ Base class for all table entries: APPID, LTYPE, LAYER, STYLE, DIMSTYLE, UCS, VIEW, VPORT, BLOCK_RECORD
    """

    def load_specific_data(self):
        bs = self.data_stream
        self.dxfattribs['name'] = bs.read_text_variable()
        bs.read_bit() << 6  # ignore bit coded value 64, see DXF Reference
        # dict `dwg_data` stores unused/ignored DWG data
        self.dwg_data['xref_index'] = bs.read_bit_short()  # xref index see ODA 20.4.66, ignore for DXF import
        self.dxfattribs['flags'] = (bs.read_bit() << 4)  # 16 = If set, table entry is externally dependent on an xref
        # loads data until: Xdep - B - 70

    def load_specific_handles(self):
        # todo: is xref_ptr dependent form flags?
        is_externally_xref_dependent = bool(self.dxfattribs['flags'] & 16)
        # if is_externally_xref_dependent:
        self.dwg_data['xref_ptr'] = self.handle_stream.read_hex_handle()


class DwgAppID(DwgTableEntry):
    # ODA chapter 20.4.66 APPID(67)
    def load_specific_data(self):
        super().load_specific_data()


class DwgTextStyle(DwgTableEntry):
    # ODA chapter 20.4.56 SHAPEFILE(53)
    def load_specific_data(self):
        super().load_specific_data()
        bs = self.data_stream
        flags = self.dxfattribs.get('flags', 0)
        flags |= (bs.read_bit() << 2)  # vertical text
        flags |= bs.read_bit()  # 1 is a shape, 0 is a font
        self.dxfattribs['flags'] = flags
        self.dxfattribs['height'] = bs.read_bit_double()  # fixed height
        self.dxfattribs['width'] = bs.read_bit_double()  # width factor
        self.dxfattribs['oblique'] = bs.read_bit_double()  # oblique angle in degrees?
        self.dxfattribs['generation_flags'] = bs.read_unsigned_byte()
        self.dxfattribs['last_height'] = bs.read_bit_double()
        self.dxfattribs['font'] = bs.read_text_variable()
        self.dxfattribs['bigfont'] = bs.read_text_variable()


class DwgLinetype(DwgTableEntry):
    # ODA chapter 20.4.58 LTYPE(57)
    def __init__(self, specs: FileHeader, data: Bytes, handle: str = ''):
        super().__init__(specs, data, handle)
        self.pattern_tags = Tags()
        self.num_dashes = 0

    def load_specific_data(self):
        super().load_specific_data()
        bs = self.data_stream
        self.dxfattribs['description'] = bs.read_text_variable()
        tags = self.pattern_tags
        pattern_length = bs.read_bit_double()
        tags.append(DXFTag(72, bs.read_unsigned_byte()))  # alignment always 'A'
        self.num_dashes = bs.read_unsigned_byte()
        tags.append(DXFTag(73, self.num_dashes))
        tags.append(DXFTag(40, pattern_length))
        for _ in range(self.num_dashes):
            pass

    def load_specific_handles(self):
        super().load_specific_handles()
        for _ in range(self.num_dashes):
            style_handle = self.handle_stream.read_hex_handle()
            self.pattern_tags.append(DXFTag(340, style_handle))

    def dxf(self, factory: 'EntityFactory'):
        entity = super().dxf(factory)
        entity.pattern_tags = self.pattern_tags
        return entity
