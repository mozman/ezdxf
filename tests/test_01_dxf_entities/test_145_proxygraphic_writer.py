import io
import json

import pytest

import ezdxf
from ezdxf.document import export_json_tags
from ezdxf.lldxf.tagger import ascii_tags_loader, binary_tags_loader, tag_compiler
from ezdxf.lldxf.tagwriter import TagCollector
from ezdxf.proxygraphic import export_proxy_graphic


def _parse_tags(data, fmt):
    if fmt == "asc":
        return list(tag_compiler(ascii_tags_loader(io.StringIO(data))))
    return list(binary_tags_loader(data))


def _line_tags(tags):
    start = next(
        i for i, tag in enumerate(tags) if tag.code == 0 and tag.value == "LINE"
    )
    stop = next(i for i in range(start + 1, len(tags)) if tags[i].code == 0)
    return tags[start:stop]


@pytest.mark.parametrize("dxfversion,length_code", [("R2010", 92), ("R2013", 160)])
@pytest.mark.parametrize("fmt", ["asc", "bin"])
@pytest.mark.parametrize("size", [0, 127, 128, 255, 256])
def test_proxy_graphic_export_preserves_binary_chunks(
    dxfversion, length_code, fmt, size
):
    data = bytes(i % 256 for i in range(size))
    chunks = [data[i : i + 127] for i in range(0, size, 127)]

    doc = ezdxf.new(dxfversion)
    line = doc.modelspace().add_line((0, 0), (1, 1))
    line.proxy_graphic = data

    stream = io.StringIO() if fmt == "asc" else io.BytesIO()
    doc.write(stream, fmt=fmt)
    tags = _line_tags(_parse_tags(stream.getvalue(), fmt))

    assert [tag.value for tag in tags if tag.code == 310] == chunks
    assert [tag.value for tag in tags if tag.code == length_code] == (
        [size] if size else []
    )

    collected = TagCollector.dxftags(line, dxfversion=doc.dxfversion)
    assert [tag.value for tag in collected if tag.code == 310] == chunks


@pytest.mark.parametrize("data_code", [310, 312])
def test_proxy_graphic_export_accepts_custom_binary_group_code(data_code):
    data = b"\x01\x02\x03\x04"
    writer = TagCollector(dxfversion="AC1024")
    export_proxy_graphic(data, writer, length_code=92, data_code=data_code)

    assert [(tag.code, tag.value) for tag in writer.tags] == [
        (92, len(data)),
        (data_code, data),
    ]


@pytest.mark.parametrize("compact", [True, False])
@pytest.mark.parametrize("data", [b"\x01\x02\x03\x04", b"ABCD", b'"', b"\\"])
def test_json_export_proxy_graphic_is_valid_and_hex_encoded(compact, data):
    doc = ezdxf.new("R2013")
    line = doc.modelspace().add_line((0, 0), (1, 1))
    line.proxy_graphic = data

    tags = json.loads(export_json_tags(doc, compact=compact))
    assert [(code, value) for code, value in tags if code == 310] == [
        (310, data.hex().upper())
    ]
    if compact:
        assert [10, [0.0, 0.0, 0.0]] in tags
    else:
        assert [10, "0.0"] in tags
