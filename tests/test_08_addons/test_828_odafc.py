from pathlib import Path

import pytest

import ezdxf
from ezdxf.addons import odafc


@pytest.mark.parametrize("failure", ["raises", "missing output", "empty output"])
def test_failed_dwg_export_preserves_existing_destination(
    tmp_path, monkeypatch, failure
):
    destination = tmp_path / "drawing.dwg"
    destination.write_bytes(b"previous drawing")
    doc = ezdxf.new()

    def run_converter(args):
        output = Path(args[1], "drawing.dwg")
        if failure == "raises":
            output.write_bytes(b"partial output")
            raise odafc.UnknownODAFCError("conversion failed")
        if failure == "empty output":
            output.touch()

    monkeypatch.setattr(odafc, "_execute_odafc", run_converter)
    with pytest.raises(odafc.UnknownODAFCError):
        odafc.export_dwg(doc, destination, replace=True)

    assert destination.read_bytes() == b"previous drawing"
    assert list(tmp_path.iterdir()) == [destination]


def test_successful_dwg_export_replaces_existing_destination(tmp_path, monkeypatch):
    destination = tmp_path / "drawing.dwg"
    destination.write_bytes(b"previous drawing")
    doc = ezdxf.new()
    doc.filename = "original.dxf"

    def run_converter(args):
        assert destination.read_bytes() == b"previous drawing"
        Path(args[1], "drawing.dwg").write_bytes(b"new drawing")

    monkeypatch.setattr(odafc, "_execute_odafc", run_converter)
    odafc.export_dwg(doc, destination, replace=True)

    assert destination.read_bytes() == b"new drawing"
    assert doc.filename == "original.dxf"
    assert list(tmp_path.iterdir()) == [destination]


def test_export_without_replace_checks_normalized_destination(tmp_path, monkeypatch):
    destination = tmp_path / "drawing.dwg"
    destination.write_bytes(b"previous drawing")

    def run_converter(args):
        pytest.fail("the converter must not run when the destination exists")

    monkeypatch.setattr(odafc, "_execute_odafc", run_converter)
    with pytest.raises(FileExistsError):
        odafc.export_dwg(ezdxf.new(), destination.with_suffix(""))

    assert destination.read_bytes() == b"previous drawing"
