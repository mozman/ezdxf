# Copyright (c) 2026, Manfred Moitzi
# License: MIT License
import os
import stat

import pytest
import ezdxf
from ezdxf import document


@pytest.mark.parametrize("fmt", ["asc", "bin"])
@pytest.mark.parametrize("version", ["R12", "R2000", "R2018"])
def test_atomic_save_round_trip(tmp_path, fmt, version):
    filename = tmp_path / "drawing.dxf"
    doc = ezdxf.new(version)
    doc.modelspace().add_line((1, 2), (3, 4))
    doc.saveas(filename, fmt=fmt)
    assert doc.filename == str(filename)
    loaded = ezdxf.readfile(filename)
    assert loaded.dxfversion == doc.dxfversion
    assert loaded.modelspace()[0].dxf.end.isclose((3, 4))
    assert set(tmp_path.iterdir()) == {filename}


@pytest.mark.parametrize("fmt", ["asc", "bin"])
@pytest.mark.parametrize("partial", [False, True])
@pytest.mark.parametrize("existing", [False, True])
def test_failed_export_preserves_destination_and_filename(
    tmp_path, monkeypatch, fmt, partial, existing
):
    filename = tmp_path / "drawing.dxf"
    if existing:
        filename.write_bytes(b"original drawing")
    doc = ezdxf.new()
    doc.filename = "previous.dxf"

    def fail(stream, fmt):
        if partial:
            stream.write("partial" if fmt == "asc" else b"partial")
        raise OSError("export failed")

    monkeypatch.setattr(doc, "write", fail)
    with pytest.raises(OSError, match="export failed"):
        doc.saveas(filename, fmt=fmt)
    assert doc.filename == "previous.dxf"
    if existing:
        assert filename.read_bytes() == b"original drawing"
    assert set(tmp_path.iterdir()) == ({filename} if existing else set())


def test_failed_replace_preserves_destination(tmp_path, monkeypatch):
    filename = tmp_path / "drawing.dxf"
    filename.write_bytes(b"original drawing")
    doc = ezdxf.new()

    def fail(*args):
        raise OSError("replace failed")

    monkeypatch.setattr(document.os, "replace", fail)
    with pytest.raises(OSError, match="replace failed"):
        doc.saveas(filename)
    assert doc.filename is None
    assert filename.read_bytes() == b"original drawing"
    assert set(tmp_path.iterdir()) == {filename}


@pytest.mark.parametrize("fmt", ["asc", "bin"])
def test_failed_close_preserves_destination(tmp_path, monkeypatch, fmt):
    filename = tmp_path / "drawing.dxf"
    filename.write_bytes(b"original drawing")
    doc = ezdxf.new()
    real_open = document.io.open

    class FailingClose:
        def __init__(self, *args, **kwargs):
            self.stream = real_open(*args, **kwargs)

        def __getattr__(self, name):
            return getattr(self.stream, name)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.stream.close()
            raise OSError("close failed")

    with monkeypatch.context() as patch:
        patch.setattr(document.io, "open", FailingClose)
        with pytest.raises(OSError, match="close failed"):
            doc.saveas(filename, fmt=fmt)
    assert doc.filename is None
    assert filename.read_bytes() == b"original drawing"
    assert set(tmp_path.iterdir()) == {filename}


def test_invalid_encoding_cleans_up_temporary_file(tmp_path):
    filename = tmp_path / "drawing.dxf"
    filename.write_bytes(b"original drawing")
    doc = ezdxf.new()
    with pytest.raises(LookupError):
        doc.saveas(filename, encoding="not-a-real-encoding")
    assert doc.filename is None
    assert filename.read_bytes() == b"original drawing"
    assert set(tmp_path.iterdir()) == {filename}


def test_invalid_format_does_not_change_destination(tmp_path):
    filename = tmp_path / "drawing.dxf"
    filename.write_bytes(b"original drawing")
    doc = ezdxf.new()
    with pytest.raises(ValueError, match="Unknown output format"):
        doc.saveas(filename, fmt="invalid")
    assert doc.filename is None
    assert filename.read_bytes() == b"original drawing"
    assert set(tmp_path.iterdir()) == {filename}


@pytest.mark.skipif(os.name == "nt", reason="POSIX permission modes")
@pytest.mark.parametrize("mode", [0o600, 0o640, 0o664])
def test_existing_file_permissions_are_preserved(tmp_path, mode):
    filename = tmp_path / "drawing.dxf"
    filename.write_bytes(b"original drawing")
    filename.chmod(mode)
    ezdxf.new().saveas(filename)
    assert stat.S_IMODE(filename.stat().st_mode) == mode


def test_new_file_uses_normal_creation_permissions(tmp_path):
    reference = tmp_path / "reference"
    reference.write_bytes(b"")
    filename = tmp_path / "drawing.dxf"
    ezdxf.new().saveas(filename)
    assert stat.S_IMODE(filename.stat().st_mode) == stat.S_IMODE(
        reference.stat().st_mode
    )


@pytest.mark.skipif(os.name == "nt", reason="requires symlink creation privilege")
@pytest.mark.parametrize("existing", [False, True])
def test_save_follows_symbolic_links(tmp_path, existing):
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    target = target_dir / "drawing.dxf"
    if existing:
        target.write_bytes(b"original drawing")
    link = tmp_path / "link.dxf"
    link.symlink_to("target/drawing.dxf")
    doc = ezdxf.new()
    doc.saveas(link)
    assert link.is_symlink()
    assert doc.filename == str(link)
    assert ezdxf.readfile(target).dxfversion == doc.dxfversion
    assert set(target_dir.iterdir()) == {target}


def test_save_rejects_directory_destination(tmp_path):
    doc = ezdxf.new()
    with pytest.raises(OSError, match="Not a regular file"):
        doc.saveas(tmp_path)
    assert doc.filename is None
    assert tmp_path.is_dir()
