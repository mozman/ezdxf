#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.dwginfo import dwg_info

R12 = "41 43 31 30 30 39"
R2000 = "41 43 31 30 31 35"
R2018 = "41 43 31 30 33 32"
R20XX = "41 43 31 30 33 33"
unknown1 = "32 32 31 30 33 32"
unknown2 = ""


def data(s) -> bytes:
    return bytes(int(x, 16) for x in s.split())


@pytest.mark.parametrize(
    "s,ver,rel",
    [
        (R12, "AC1009", "R12"),
        (R2000, "AC1015", "R2000"),
        (R2018, "AC1032", "R2018"),
        (R20XX, "AC1033", "unknown"),
    ],
    ids=["R12", "R2000", "R2018", "unknown"],
)
def test_detect(s, ver, rel):
    info = dwg_info(data(s))
    assert info.version == ver
    assert info.release == rel


@pytest.mark.parametrize(
    "s", [unknown1, unknown2],
    ids=["invalid", "empty"],
)
def test_detect_invalid(s):
    info = dwg_info(data(s))
    assert info.version == "invalid"
    assert info.release == "invalid"


if __name__ == "__main__":
    pytest.main([__file__])
