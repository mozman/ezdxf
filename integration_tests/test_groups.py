#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import pytest
import ezdxf

DATA = Path(__file__).parent / "data"
GROUPS = "groups.dxf"


@pytest.fixture
def doc():
    return ezdxf.readfile(DATA / GROUPS)


def test_load_dxf_with_groups(doc):
    assert len(doc.groups) == 2
    (name1, g1), (name2, g2) = doc.groups
    assert name1 == "G1"
    assert len(g1) == 5
    assert name2 == "G2"
    assert len(g2) == 8


def delete_G1_content(dxf):
    g1 = dxf.groups.get("G1")
    for entity in g1:
        entity.destroy()


def test_delete_group_content_and_export_dxf(doc, tmp_path):
    delete_G1_content(doc)
    doc.saveas(tmp_path / GROUPS)
    assert True is True, "saveas() should not raise an exception"


def test_reload_dxf_with_empty_group_content(doc, tmp_path):
    delete_G1_content(doc)
    doc.saveas(tmp_path / GROUPS)
    del doc

    reload = ezdxf.readfile(tmp_path / GROUPS)
    assert len(reload.groups) == 2
    (name1, g1), (name2, g2) = reload.groups
    assert name1 == "G1"
    assert len(g1) == 0, "empty group still exist"
    assert name2 == "G2"
    assert len(g2) == 8


if __name__ == "__main__":
    pytest.main([__file__])
