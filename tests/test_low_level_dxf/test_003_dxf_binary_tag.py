# Copyright (c) 2018-2019 Manfred Moitzi
# License: MIT License
from ezdxf.lldxf.types import DXFBinaryTag, encode_hex_code_string_to_bytes


def test_init():
    tag = DXFBinaryTag.from_string(310, 'FFFF')
    assert tag == (310, b"\xff\xff")

    tag = DXFBinaryTag(310, b"\xff\xff")
    assert tag == (310, b"\xff\xff")

    tag2 = DXFBinaryTag.from_string(code=310, value='FFFF')
    assert tag2 == (310, b"\xff\xff")


def test_index_able():
    tag = DXFBinaryTag.from_string(310, 'FFFF')
    assert tag[0] == 310
    assert tag[1] == b"\xff\xff"


def test_dxf_str():
    assert DXFBinaryTag.from_string(310, 'FFFF').tostring() == "FFFF"
    assert DXFBinaryTag.from_string(310, 'FFFF').dxfstr() == "310\nFFFF\n"


def test_long_string():
    tag = DXFBinaryTag.from_string(310, '414349532042696E61727946696C652855000000000000020000000C00000007104175746F6465736B204175746F434144071841534D203231392E302E302E3536303020556E6B6E6F776E071853756E204D61792020342031353A34373A3233203230313406000000000000F03F068DEDB5A0F7C6B03E06BBBDD7D9DF7CDB')
    assert len(tag.value) == 127
    clone = tag.clone()
    assert tag.value == clone.value


def test_encode_hex_code_string():
    import array
    s = ''.join('%0.2X' % byte for byte in range(256))
    assert len(s) == 512
    bytes_ = encode_hex_code_string_to_bytes(s)
    assert len(bytes_) == 256
    # works in Python 2.7 & Python 3
    for x, y in zip(array.array('B', bytes_), range(256)):
        assert x == y
    tag = DXFBinaryTag(310, bytes_)
    assert tag.tostring() == s
