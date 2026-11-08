#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
import os
import pytest
import ezdxf

BASEDIR = os.path.dirname(__file__)
DATADIR = "data"


@pytest.fixture(
    params=[
        "bin_dxf_r14.dxf",
        "bin_dxf_r13.dxf",
    ]
)
def filename(request):
    filename = os.path.join(BASEDIR, DATADIR, request.param)
    if not os.path.exists(filename):
        pytest.skip("File {} not found.".format(filename))
    return filename


def test_open_R13_R14(filename, tmpdir):
    doc = ezdxf.readfile(filename)
    assert "Model" in doc.layouts, "Model space not found"
    assert "Layout1" in doc.layouts, "Paper space not found"
    assert doc.dxfversion >= "AC1015"
    msp = doc.modelspace()
    msp.add_line((0, 0), (10, 3))
    converted = str(tmpdir.join("converted_AC1015.dxf"))
    doc.saveas(converted)
    assert os.path.exists(converted)


def test_open_R2000_with_xdata():
    filename = os.path.join(BASEDIR, DATADIR, "bin_dxf_r2000.dxf")
    doc = ezdxf.readfile(filename)
    assert "Model" in doc.layouts, "Model space not found"
    assert "Layout1" in doc.layouts, "Paper space not found"
    assert doc.dxfversion == "AC1015"
    msp = doc.modelspace()
    text = msp.query("TEXT").first
    assert text.dxf.text == "ezdxf"
    hyperlink, description, location = text.get_hyperlink()
    assert hyperlink == "http://ezdxf.mozman.at"
    msp.add_line((0, 0), (10, 3))


def test_open_R12():
    filename = os.path.join(BASEDIR, DATADIR, "bin_dxf_r12.dxf")
    doc = ezdxf.readfile(filename)
    assert "Model" in doc.layouts, "Model space not found"
    assert "Layout1" in doc.layouts, "Paper space not found"
    assert doc.dxfversion == "AC1009"


def test_audit_command_accepts_binary_DXF_files(capsys):
    from argparse import Namespace
    from ezdxf.commands import Audit

    filename = os.path.join(BASEDIR, DATADIR, "bin_dxf_r2000.dxf")
    Audit.run(Namespace(files=[filename], save=False, explore=False))
    output = capsys.readouterr().out
    assert "is not a DXF file" not in output
    assert "Invalid or corrupted DXF file" not in output


def test_load_document_of_commands_opens_binary_DXF_files():
    from ezdxf.commands import load_document

    filename = os.path.join(BASEDIR, DATADIR, "bin_dxf_r2000.dxf")
    doc, auditor = load_document(filename)
    assert "Model" in doc.layouts
    assert "Layout1" in doc.layouts
