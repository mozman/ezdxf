# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
from io import BytesIO
from ezdxf.recover import (
    bytes_loader,
    detect_encoding,
    synced_bytes_loader,
    _detect_dxf_version,
    _search_int,
    _search_float,
    byte_tag_compiler,
)
from ezdxf.lldxf import const

HEADER = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1027
  9
$ACADMAINTVER
 70
105
  9
$DWGCODEPAGE
  3
ANSI_1252
  9
TEST
  1
ÄÖÜ
"""

MALFORMED_GROUP_CODES = b"""  0x
SECTION
  +2x
HEADER
  \t9\t
$ACADVER
  1.0
AC1027
"""


class TestBytesLoader:
    @pytest.fixture(params=[bytes_loader, synced_bytes_loader])
    def loader(self, request):
        return request.param

    @pytest.fixture
    def data(self):
        return BytesIO(HEADER.encode("latin1"))

    def test_bytes_loader(self, data, loader):
        result = list(loader(data))
        assert len(result) == 10
        assert result[-1] == (1, b"\xc4\xd6\xdc")

    def test_encoding_detector(self, data, loader):
        assert detect_encoding(loader(data)) == "utf8"

    def test_windows_line_endings_CR_LF(self, loader):
        tags = list(loader(BytesIO(b"0\r\n1\r\n0\r\n2\r\n")))
        assert tags == [
            (0, b"1"),
            (0, b"2"),
        ], "Windows line endings CR/LF must be supported."

    def test_linux_and_macos_x_line_endings_LF(self, loader):
        tags = list(bytes_loader(BytesIO(b"0\n1\n0\n2\n")))
        assert tags == [
            (0, b"1"),
            (0, b"2"),
        ], "Linux and MacOS X line endings LF must be supported."

    def test_line_endings_only_CR(self):
        assert (
            list(synced_bytes_loader(BytesIO(b"0\r1\r0\r2\r"))) == []
        ), "MacOS prior to MacOS X line endings CR are not supported."

    def test_malformed_group_codes(self, loader):
        data = BytesIO(MALFORMED_GROUP_CODES)
        tags = list(loader(data))
        assert tags[0] == (0, b"SECTION")
        assert tags[1] == (2, b"HEADER")
        assert tags[2] == (9, b"$ACADVER")
        assert tags[3] == (1, b"AC1027")


MALFORMED_VALUE_TAGS = b"""  70 # int value
  42xyz
40 # float value
  47.11xyz
10 # 3D vertex
 1.0x
20
 1.0y
30
 1.0z
11 # 2D vertex
 2.0x
21
 2.0y
 0
DUMMY
"""


class TestByteTagCompiler:
    def test_malformed_value_tags(self):
        loader = bytes_loader(BytesIO(MALFORMED_VALUE_TAGS))
        tags = list(byte_tag_compiler(loader))
        assert tags[0] == (70, 42)
        assert tags[1] == (40, 47.11)
        assert tags[2] == (10, (1, 1, 1))
        assert tags[3] == (11, (2, 2))


OUT_OF_SYNC_TAGS = """
  0
SECTION
  2
HEADER

  9
$ACADVER
  1
AC1027
  9
$ACADMAINTVER
 70
105
  9
$DWGCODEPAGE

  3
ANSI_1252
  9
TEST
  1
test
"""


def test_out_of_sync_tags():
    result = list(synced_bytes_loader(BytesIO(OUT_OF_SYNC_TAGS.encode())))
    assert len(result) == 10


class TestDetectDXFVersion:
    def test_missing_dxf_version_is_r12(self):
        assert _detect_dxf_version([]) == "AC1009"

    def test_detect_r12(self):
        assert _detect_dxf_version([(9, "$ACADVER"), (3, "AC1009")]) == "AC1009"

    @pytest.mark.parametrize("ver", list(const.acad_release.keys()))
    def test_detect_all_supported_versions(self, ver):
        assert _detect_dxf_version([(9, "$ACADVER"), (3, ver)]) == ver

    def test_detect_any_well_formed_version(self):
        assert _detect_dxf_version([(9, "$ACADVER"), (3, "AC9999")]) == "AC9999"

    @pytest.mark.parametrize(
        "ver", ["AC10x9", "XC1009", "0000", "AC10240", 0, None]
    )
    def test_malformed_version_is_r12(self, ver):
        assert _detect_dxf_version([(9, "$ACADVER"), (3, ver)]) == "AC1009"

    @pytest.mark.parametrize(
        "ver",
        [
            " AC1015",
            "AC1015 ",
            "  AC1015  ",
        ],
    )
    def test_strip_whitespace_from_version_string(self, ver):
        assert _detect_dxf_version([(9, "$ACADVER"), (3, ver)]) == "AC1015"


class TestSearchIntConverter:
    @pytest.mark.parametrize("s", ["0", "00", "+0", "-0"])
    def test_valid_zero_int(self, s):
        assert _search_int(s) == 0

    @pytest.mark.parametrize("s", ["+1", "1", "01"])
    def test_valid_int(self, s):
        assert _search_int(s) == 1

    @pytest.mark.parametrize("s", [" 1", "\t1", "\r1", " \r1"])
    def test_ignore_whitespace_in_front_of_int(self, s):
        assert _search_int(s) == 1

    @pytest.mark.parametrize("s", ["1 ", "1\t", "1\r", "1 \r"])
    def test_ignore_whitespace_behind_int(self, s):
        assert _search_int(s) == 1

    @pytest.mark.parametrize(
        "s",
        [
            "1.",
            "1,",
            "1a",
            "1-",
            "1+",
            "1$",
            "1 1",
            "+1 x fd fgg",
            "\t\r+1_ ",
        ],
    )
    def test_ignore_invalid_chars_behind_int(self, s):
        assert _search_int(s) == 1

    @pytest.mark.parametrize(
        "b",
        [
            b"1.",
            b"1,",
            b"1a",
            b"1-",
            b"\t\r+1_ ",
        ],
    )
    def test_if_works_with_bytes(self, b):
        assert _search_int(b) == 1


class TestSearchFloatConverter:
    @pytest.mark.parametrize("s", ["0", "0.0", "+0.", "-0."])
    def test_valid_zero(self, s):
        assert _search_float(s) == 0.0

    @pytest.mark.parametrize(
        "s",
        ["1", "+1", "1.", "1.0", "1e0", "1.e0", "1.0e0", "1E0", "1e+0", "1e-0"],
    )
    def test_valid_positive_floats(self, s):
        assert _search_float(s) == 1.0

    @pytest.mark.parametrize(
        "s",
        [
            "-1",
            "-1.",
            "-1.0",
            "-1e0",
            "-1.e0",
            "-1.0e0",
        ],
    )
    def test_valid_negative_floats(self, s):
        assert _search_float(s) == -1.0

    def test_negative_exponent(self):
        assert _search_float("1e-1") == 0.1
        assert _search_float("-1e-1") == -0.1

    @pytest.mark.parametrize("s", [" 1.0", "\t1.0", "\r1.0", " \r1.0"])
    def test_ignore_whitespace_in_front_of_float(self, s):
        assert _search_float(s) == 1.0

    @pytest.mark.parametrize("s", ["1.0 ", "1.\t", "1.\r", "1. \r", "1e0 \t"])
    def test_ignore_whitespace_behind_float(self, s):
        assert _search_float(s) == 1.0

    @pytest.mark.parametrize(
        "s",
        [
            "1,",
            "1a",
            "1-",
            "1+",
            "1$",
            "1 1",
            "+1 x fd fgg",
            "\t\r+1_ ",
            "1.,",
            "1.a",
            "1.-",
            "1.+",
            "1.$",
            "1. 1",
            "+1. x fd fgg",
            "\t\r+1._ ",
            "1e0,",
            "1e0a",
            "1e0-",
            "1e0+",
            "1e0$",
            "1e0 1",
            "+1e0 x fd fgg",
            "\t\r+1e0_ ",
            "  1e+0xx",
            "  1e-0xx",
            "  1E+0xx",
            "  1E-0xx",
        ],
    )
    def test_ignore_invalid_chars_behind_float(self, s):
        assert _search_float(s) == 1.0

    @pytest.mark.parametrize(
        "b",
        [
            b"1,",
            b"1a",
            b"1-",
            b"1+",
            b"1$",
            b"1 1",
            b"+1 x fd fgg",
            b"\t\r+1_ ",
        ],
    )
    def test_if_works_bytes(self, b):
        assert _search_float(b) == 1.0
