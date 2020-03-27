# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Optional
from ezdxf.lldxf.const import DXF12
from ezdxf.tools.binarydata import bytes_to_hexstr

if TYPE_CHECKING:
    from ezdxf.eztypes import Tags, TagWriter

CHUNK_SIZE = 128


def load_proxy_graphic(tags: 'Tags') -> Optional[bytes]:
    binary_data = [tag.value for tag in tags.pop_tags(codes=(92, 310)) if tag.code == 310]
    return b''.join(binary_data) if len(binary_data) else None


def export_proxy_graphic(data: bytes, tagwriter: 'TagWriter') -> None:
    # Do not export proxy graphic for DXF R12 files
    assert tagwriter.dxfversion > DXF12

    length = len(data)
    if length == 0:
        return

    tagwriter.write_tag2(92, length)
    index = 0
    while index < length:
        hex_str = bytes_to_hexstr(data[index:index + CHUNK_SIZE])
        tagwriter.write_tag2(310, hex_str)
        index += CHUNK_SIZE
