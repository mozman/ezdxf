#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
import ezdxf


def write_dxf_file(filename):
    doc = ezdxf.new("R12")
    doc.header["$HANDLING"] = 0
    msp = doc.modelspace()
    msp.add_line((0, 0), (1, 0))
    doc.saveas(filename)


def test_read_file_without_handles(tmpdir):
    filename = tmpdir.join("r12_without_handles.dxf")
    write_dxf_file(filename)

    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()
    line = msp.query("LINE").first
    assert line is not None
    assert line.dxf.handle is not None
