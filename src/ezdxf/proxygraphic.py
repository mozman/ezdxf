# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Optional
import struct
from ezdxf.lldxf.const import DXF12
from ezdxf.tools.binarydata import bytes_to_hexstr

if TYPE_CHECKING:
    from ezdxf.eztypes import Tags, TagWriter

CHUNK_SIZE = 127


def load_proxy_graphic(tags: 'Tags', length_code: int = 160, data_code: int = 310) -> Optional[bytes]:
    binary_data = [tag.value for tag in tags.pop_tags(codes=(length_code, data_code)) if tag.code == data_code]
    return b''.join(binary_data) if len(binary_data) else None


def export_proxy_graphic(data: bytes, tagwriter: 'TagWriter', length_code: int = 160, data_code: int = 310) -> None:
    # Do not export proxy graphic for DXF R12 files
    assert tagwriter.dxfversion > DXF12

    length = len(data)
    if length == 0:
        return

    tagwriter.write_tag2(length_code, length)
    index = 0
    while index < length:
        hex_str = bytes_to_hexstr(data[index:index + CHUNK_SIZE])
        tagwriter.write_tag2(data_code, hex_str)
        index += CHUNK_SIZE
