#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
import pytest
import os
from io import StringIO
import ezdxf
from ezdxf.lldxf.tagwriter import TagWriter

CIVIL_3D = os.path.join(
    ezdxf.EZDXF_TEST_FILES, "AutodeskProducts/Civil3D_2018.dxf"
)


@pytest.fixture(scope="module")
def doc():
    try:
        # Recover mode is not necessary:
        return ezdxf.readfile(CIVIL_3D)
    except IOError:
        pytest.skip(f'File "{CIVIL_3D}" not found.')


@pytest.mark.parametrize("handle", ["22C1", "22C4", "22C7"])
def test_civil_3d_preserves_binary_data_in_xrecords(doc, handle):
    # Civil 3D stores binary data in XRECORDS as group code 300:
    xrecord = doc.entitydb[handle]
    bin_data = xrecord.tags[1]
    assert bin_data.code == 300
    data = bin_data.value.encode("utf8", errors="surrogateescape")
    assert b"\xed\xb7\x9d" in data, "expected preserved binary data"


BASEDIR = os.path.dirname(__file__)
DATADIR = "data"


@pytest.mark.parametrize(
    ("handle", "n"), [("22C1", 0), ("22C4", 1), ("22C7", 2)]
)
def test_dxf_export_xrecords_with_binary_data(doc, handle, n):
    def expected():
        filename = os.path.join(BASEDIR, DATADIR, f"XRECORD_{n}.bin")
        if not os.path.exists(filename):
            pytest.skip(f"File {filename} not found.")
        with open(filename, "rb") as fp:
            # normalize line endings and remove spaces
            return fp.read().replace(b"\r\n", b"\n").replace(b" ", b"")

    stream = StringIO()
    writer = TagWriter(stream)

    xrecord = doc.entitydb[handle]
    xrecord.export_dxf(writer)

    # remove spaces
    data = doc.encode(stream.getvalue()).replace(b" ", b"")
    assert data == expected()
