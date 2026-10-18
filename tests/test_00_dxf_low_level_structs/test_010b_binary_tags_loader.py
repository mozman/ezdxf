# Copyright (c) 2026, Manfred Moitzi
# License: MIT License
import io

import pytest

from ezdxf.lldxf.const import DXFStructureError
from ezdxf.lldxf.tagger import binary_tags_loader
from ezdxf.lldxf.tagwriter import BinaryTagWriter

VERSIONS = ["AC1009", "AC1015", "AC1032"]
SIGNATURE = b"AutoCAD Binary DXF\r\n\x1a\x00"


def make_stream(version):
    stream = io.BytesIO()
    writer = BinaryTagWriter(stream, dxfversion=version)
    writer.write_signature()
    writer.write_tag2(9, "$ACADVER")
    writer.write_tag2(1, version)
    writer.write_tag2(9, "$DWGCODEPAGE")
    writer.write_tag2(3, "ANSI_1252")
    return stream, writer


@pytest.mark.parametrize("version", VERSIONS)
@pytest.mark.parametrize(
    "code, value",
    [
        (1, "hello"),
        (40, 1.25),
        (70, -12),
        (90, 12345),
        (160, 2**40),
        (1004, b"abcde"),
        (1000, "extended"),
    ],
)
def test_truncation_at_every_tag_byte(version, code, value):
    stream, writer = make_stream(version)
    start = stream.tell()
    writer.write_tag2(code, value)
    data = stream.getvalue()
    assert list(binary_tags_loader(data))[-1] == (code, value)
    # Ending at a complete tag boundary is valid for this low-level loader.
    assert len(list(binary_tags_loader(data[:start]))) == 4
    for end in range(start + 1, len(data)):
        with pytest.raises(DXFStructureError, match="byte"):
            list(binary_tags_loader(data[:end]))


@pytest.mark.parametrize("version", ["AC1015", "AC1032"])
@pytest.mark.parametrize("code, value", [(290, 1), (310, b"abcde")])
def test_truncation_of_modern_only_tags(version, code, value):
    stream, writer = make_stream(version)
    start = stream.tell()
    writer.write_tag2(code, value)
    data = stream.getvalue()
    assert list(binary_tags_loader(data))[-1] == (code, value)
    for end in range(start + 1, len(data)):
        with pytest.raises(DXFStructureError, match="byte"):
            list(binary_tags_loader(data[:end]))


@pytest.mark.parametrize("version", VERSIONS)
def test_header_truncation_never_leaks_index_or_struct_errors(version):
    stream, _ = make_stream(version)
    data = stream.getvalue()
    for end in range(len(data)):
        try:
            list(binary_tags_loader(data[:end]))
        except DXFStructureError:
            pass


def test_header_version_name_at_end_of_scan_window():
    stream = io.BytesIO()
    writer = BinaryTagWriter(stream, dxfversion="AC1015")
    writer.write_signature()
    writer.write_tag2(1, "x" * 989)
    writer.write_tag2(9, "$ACADVER")
    writer.write_tag2(1, "AC1015")
    writer.write_tag2(0, "EOF")
    data = stream.getvalue()
    assert data.index(b"$ACADVER") == 1016
    assert list(binary_tags_loader(data)) == [
        (1, "x" * 989),
        (9, "$ACADVER"),
        (1, "AC1015"),
        (0, "EOF"),
    ]


@pytest.mark.parametrize("version", VERSIONS)
@pytest.mark.parametrize(
    "variable, value", [("$ACADVER", "AC1009"), ("$DWGCODEPAGE", "ANSI_1252")]
)
def test_unterminated_header_value_raises_structure_error(version, variable, value):
    stream = io.BytesIO()
    writer = BinaryTagWriter(stream, dxfversion=version)
    writer.write_signature()
    writer.write_tag2(9, variable)
    writer.write_tag2(1 if variable == "$ACADVER" else 3, value)
    with pytest.raises(DXFStructureError, match="header variable"):
        list(binary_tags_loader(stream.getvalue()[:-1]))


def test_r12_extended_code_truncation():
    for data in [SIGNATURE + b"\xff", SIGNATURE + b"\xff\xec"]:
        with pytest.raises(DXFStructureError, match="group code at byte 22"):
            list(binary_tags_loader(data))


@pytest.mark.parametrize("version", VERSIONS)
def test_declared_binary_chunk_length_is_enforced(version):
    stream, writer = make_stream(version)
    writer.write_tag2(1004, b"abcde")
    with pytest.raises(DXFStructureError, match="group code 1004"):
        list(binary_tags_loader(stream.getvalue()[:-3]))


@pytest.mark.parametrize("version", VERSIONS)
def test_unicode_decoding_error_remains_distinct(version):
    stream, writer = make_stream(version)
    writer.write_tag2(1, "PLACEHOLDER")
    data = stream.getvalue().replace(b"PLACEHOLDER", b"\x81")
    with pytest.raises(UnicodeDecodeError):
        list(binary_tags_loader(data, errors="strict"))
    assert list(binary_tags_loader(data))[-1] == (1, "\udc81")


@pytest.mark.parametrize("version", VERSIONS)
def test_zero_length_binary_chunk_is_valid(version):
    stream, _ = make_stream(version)
    code = (b"\xff" if version == "AC1009" else b"") + b"\xec\x03"
    assert list(binary_tags_loader(stream.getvalue() + code + b"\x00"))[-1] == (
        1004,
        b"",
    )
