# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
from pathlib import Path
from ezdxf.addons.dwg.loader import DwgDocument
from ezdxf.addons.dwg.header_section import (
    load_commands,
    HEADER_DESCRIPTION,
    CMD_SET_VERSION,
    CMD_SKIP_BITS,
    CMD_SKIP_NEXT_IF,
    CMD_SET_VAR,
    ACAD_LATEST,
)
from ezdxf.addons.dwg.crc import crc8, crc32

FILE1 = Path(__file__).parent / "807_1.dwg"
pytestmark = pytest.mark.skipif(
    not FILE1.exists(), reason=f"Data file '{FILE1}' not present."
)


@pytest.fixture(scope="module")
def dwg1() -> bytes:
    return FILE1.read_bytes()


def test_load_classes(dwg1):
    doc = DwgDocument(dwg1, crc_check=True)
    doc.load()
    assert len(doc.dxf_object_types) == 15
    assert doc.dxf_object_types[500] == "ACDBDICTIONARYWDFLT"
    assert doc.dxf_object_types[514] == "LAYOUT"

    classes = doc.doc.classes
    cls_dict = classes.classes
    assert len(cls_dict) == 15
    assert classes.get("ACDBDICTIONARYWDFLT") is not None
    assert classes.get("LAYOUT") is not None


def test_header_commands():
    assert load_commands("ver: all") == [
        (CMD_SET_VERSION, ("AC1012", ACAD_LATEST))
    ]
    assert load_commands("ver: R13") == [
        (CMD_SET_VERSION, ("AC1012", "AC1012"))
    ]
    assert load_commands("ver: R2000") == [
        (CMD_SET_VERSION, ("AC1015", "AC1015"))
    ]
    assert load_commands("ver: R2004+") == [
        (CMD_SET_VERSION, ("AC1018", ACAD_LATEST))
    ]
    assert load_commands("ver: R13 - R14  # comment") == [
        (CMD_SET_VERSION, ("AC1012", "AC1014"))
    ]
    assert load_commands("$TEST: H  # comment") == [
        (CMD_SET_VAR, ("$TEST", "H"))
    ]
    assert load_commands("$TEST : BLL") == [(CMD_SET_VAR, ("$TEST", "BLL"))]
    assert load_commands("skip_bits : 7") == [(CMD_SKIP_BITS, "7")]
    assert load_commands("skip_next_if: 1 == 1\n$TEST : BLL") == [
        (CMD_SKIP_NEXT_IF, "1 == 1"),
        (CMD_SET_VAR, ("$TEST", "BLL")),
    ]


def test_load_all():
    commands = load_commands(HEADER_DESCRIPTION)
    assert len(commands) > 0


def test_crc8_is_runnable():
    result = crc8(b"mozman")
    assert bool(result)


def test_crc32_is_runnable():
    result = crc32(b"mozman")
    assert bool(result)


def test_parse_hex_dump():
    from ezdxf.tools.test import parse_hex_dump

    result = parse_hex_dump(R14_TEST_HDR)
    assert len(result) == 584


R14_TEST_HDR = """
00000 41 43 31 30 31 34 00 00
00008 00 00 00 00 01 3F 0C 00
00010 00 00 00 1E 00 05 00 00
00018 00 00 58 00 00 00 ED 01
00020 00 00 01 45 02 00 00 26
00028 00 00 00 02 27 0B 00 00
00030 50 00 00 00 03 77 0B 00
00038 00 35 00 00 00 04 3B 0C
00040 00 00 04 00 00 00 2D 5C
00048 95 A0 4E 28 99 82 1A E5
00050 5E 41 E0 5F 9D 3A 4D 00
00058 CF 7B 1F 23 FD DE 38 A9
00060 5F 7C 68 B8 4E 6D 33 5F
00068 C7 01 00 00 00 00 07 00
00070 1F BF 55 D0 95 40 5B 6A
00078 51 A9 43 1A 65 AC 40 50
00080 23 30 2D 02 41 2A 40 50
00088 19 01 AA 90 84 19 06 41
00090 90 64 19 06 40 D4 69 30
00098 41 24 C9 26 A6 66 66 66
000A0 66 72 4F C9 A9 99 99 99
000A8 99 9A 93 F2 6A 66 66 66
000B0 66 66 E4 FC 00 00 00 00
000B8 00 00 E0 3F AA AA 80 00
000C0 00 00 00 00 0E 03 F0 00
000C8 00 00 00 00 03 80 FD 80
000D0 00 00 00 00 00 0E 03 F5
000D8 40 4B 8B 56 52 50 02 D1
000E0 A6 00 08 B5 65 25 00 20
000E8 29 E0 00 A3 30 F4 00 02
000F0 33 0F 40 00 30 14 D5 10
000F8 F5 11 05 11 45 11 D5 11
00100 CA 84 08 CB 57 81 DA F1
00108 54 41 02 32 D5 E0 76 BC
00110 55 10 40 8C B5 78 1D AF
00118 15 44 10 23 2D 5E 07 6B
00120 C5 71 04 08 CB 57 81 DA
00128 F1 5C 41 02 32 D5 E0 76
00130 BC 57 10 00 00 00 00 00
00138 00 00 00 00 00 00 00 00
00140 00 00 00 00 00 00 00 00
00148 00 A1 00 00 00 00 00 00
00150 00 89 02 A9 A9 94 2A 10
00158 23 2D 5E 07 6B C5 51 04
00160 08 CB 57 81 DA F1 54 41
00168 02 32 D5 E0 76 BC 55 10
00170 40 8C B5 78 1D AF 15 C4
00178 10 23 2D 5E 07 6B C5 71
00180 04 08 CB 57 81 DA F1 5C
00188 40 00 00 00 00 00 00 00 
00190 00 00 00 00 00 00 00 00
00198 00 00 00 00 00 00 02 84 
001A0 00 00 00 00 00 00 02 24 
001A8 0A A6 A6 50 30 00 40 00 
001B0 08 00 18 00 00 00 01 02
001B8 90 44 11 02 40 94 44 10
001C0 2B 5E 8D C0 F4 2B 1C FC
001C8 00 00 00 00 00 00 B0 3F
001D0 14 AE 07 A1 7A D4 76 0F
001D8 C0 AD 7A 37 03 D0 AC 73 
001E0 FA A0 2B 5E 8D C0 F4 2B 
001E8 1C FC 0A D7 A3 70 3D 0A 
001F0 B7 3F 86 66 66 66 66 66 
001F8 63 94 06 40 AD 7A 37 03 
00200 D0 AB 73 FA AA A3 10 13 
00208 10 23 10 33 10 53 10 63 
00210 10 73 10 83 10 93 10 A3 
00218 10 B5 10 D5 10 E3 10 C5 
00220 11 65 11 95 11 45 11 35 
00228 11 51 D5 58 D4 A0 34 26 
00230 4B 76 E0 5B 27 30 84 E0 
00238 DC 02 21 C7 56 A0 83 97 
00240 47 B1 92 CC A0 00 00 00
"""

if __name__ == "__main__":
    pytest.main([__file__])
