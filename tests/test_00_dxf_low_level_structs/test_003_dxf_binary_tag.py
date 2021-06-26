# Copyright (c) 2018-2019 Manfred Moitzi
# License: MIT License
from binascii import unhexlify
from ezdxf.lldxf.types import DXFBinaryTag
from ezdxf.lldxf.tags import binary_data_to_dxf_tags


def test_init():
    tag = DXFBinaryTag.from_string(310, "FFFF")
    assert tag == (310, b"\xff\xff")

    tag = DXFBinaryTag(310, b"\xff\xff")
    assert tag == (310, b"\xff\xff")

    tag2 = DXFBinaryTag.from_string(code=310, value="FFFF")
    assert tag2 == (310, b"\xff\xff")


def test_index_able():
    tag = DXFBinaryTag.from_string(310, "FFFF")
    assert tag[0] == 310
    assert tag[1] == b"\xff\xff"


def test_dxf_str():
    assert DXFBinaryTag.from_string(310, "FFFF").tostring() == "FFFF"
    assert DXFBinaryTag.from_string(310, "FFFF").dxfstr() == "310\nFFFF\n"


def test_long_string():
    tag = DXFBinaryTag.from_string(
        310,
        "414349532042696E61727946696C652855000000000000020000000C00000007104175746F6465736B204175746F434144071841534D203231392E302E302E3536303020556E6B6E6F776E071853756E204D61792020342031353A34373A3233203230313406000000000000F03F068DEDB5A0F7C6B03E06BBBDD7D9DF7CDB",
    )
    assert len(tag.value) == 127
    clone = tag.clone()
    assert tag.value == clone.value


def test_hexstr_to_bytes():
    import array

    s = "".join("%0.2X" % byte for byte in range(256))
    assert len(s) == 512
    bytes_ = unhexlify(s)
    assert len(bytes_) == 256
    for x, y in zip(array.array("B", bytes_), range(256)):
        assert x == y
    tag = DXFBinaryTag(310, bytes_)
    assert tag.tostring() == s


class TestBinaryDataToDXFTags:
    def test_for_preceding_length_tag(self):
        tags = binary_data_to_dxf_tags(b"0123456789")
        assert tags[0] == (160, 10)

    def test_if_data_tag_values_are_bytes(self):
        tags = binary_data_to_dxf_tags(b"0123456789")
        assert isinstance(tags[1].value, bytes)

    def test_if_empty_data_creates_a_length_tag(self):
        tags = binary_data_to_dxf_tags(b"")
        assert tags[0] == (160, 0)

    def test_if_tag_value_size_is_limited_to_chunk_size(self):
        data = b"0123456789" * 10
        tags = binary_data_to_dxf_tags(data, value_size=10)
        assert len(tags) == 11
        assert tags[0] == (160, 100)
        assert all(len(t.value) == 10 for t in tags[1:])

    def test_if_merged_tag_values_matches_source_data(self):
        data = b"0123456789" * 10
        tags = binary_data_to_dxf_tags(data, value_size=10)
        content = b"".join(t.value for t in tags[1:])
        assert data == content

