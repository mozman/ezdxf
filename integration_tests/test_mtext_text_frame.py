#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable, cast
from pathlib import Path
import pytest
import ezdxf
from ezdxf import recover
from ezdxf.entities import MText

DATA = Path(__file__).parent / "data"
TEXT_FRAME = "mtext_text_frame.dxf"


def load_mtext_entities(name: str):
    doc = ezdxf.readfile(DATA / name)
    return doc


def recover_mtext_entities(name: str):
    doc, auditor = recover.readfile(DATA / name)
    return doc


@pytest.fixture(scope="module", params=["load", "recover"])
def doc(request):
    if request.param == "load":
        return load_mtext_entities(TEXT_FRAME)
    elif request.param == "recover":
        return recover_mtext_entities(TEXT_FRAME)


def test_remove_mtext_text_frame_at_loading_stage(doc):
    msp = doc.modelspace()
    assert (
        len(msp.query("LWPOLYLINE")) == 0
    ), "text frame entities should be removed"
    mtext = msp.query("MTEXT").first
    assert bool(mtext.dxf.bg_fill & 16) is True


def test_remove_column_text_frames_at_loading_stage():
    doc = ezdxf.readfile(DATA / "mtext_framed_columns.dxf")
    msp = doc.modelspace()
    assert (
        len(msp.query("LWPOLYLINE")) == 0
    ), "text frame entities should be removed"


def test_do_not_export_mtext_text_borders(tmp_path):
    doc1 = ezdxf.readfile(DATA / TEXT_FRAME)
    doc1.saveas(tmp_path / TEXT_FRAME)
    doc2 = ezdxf.readfile(tmp_path / TEXT_FRAME)
    msp = doc2.modelspace()
    assert (
        len(msp.query("LWPOLYLINE")) == 0
    ), "text frame entities should be removed"
    mtext = msp.query("MTEXT").first
    assert mtext.xdata is None, "XDATA for MTEXT_TEXT_BORDERS should be removed"
    assert bool(mtext.dxf.bg_fill & 16) is True


if __name__ == "__main__":
    pytest.main([__file__])
