#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf


def test_reset_layout1_landscape():
    doc = ezdxf.new()
    assert len(doc.layouts) == 2
    psp = doc.page_setup("Layout1", fmt="ISO A0")
    assert len(doc.layouts) == 2
    assert psp.dxf_layout.dxf.paper_width == 1189
    assert psp.dxf_layout.dxf.paper_height == 841


def test_invalid_paper_format_returns_A3():
    doc = ezdxf.new()
    with pytest.raises(ValueError):
        doc.page_setup("Layout1", fmt="INVALID")


def test_reset_layout1_portrait():
    doc = ezdxf.new()
    assert len(doc.layouts) == 2
    psp = doc.page_setup("Layout1", fmt="ISO A0", landscape=False)
    assert len(doc.layouts) == 2
    assert psp.dxf_layout.dxf.paper_width == 841
    assert psp.dxf_layout.dxf.paper_height == 1189


def test_resetting_layout1_creates_a_new_main_viewport():
    doc = ezdxf.new()
    psp = doc.paperspace("Layout1")
    assert len(psp) == 0  # no main viewport exist, not required
    psp = doc.page_setup("Layout1", fmt="ISO A0")
    assert len(psp.query("VIEWPORT")) == 1


def test_resetting_layout1_does_not_delete_entities():
    doc = ezdxf.new()
    psp = doc.paperspace("Layout1")
    psp.add_point((0, 0))
    assert len(psp) == 1
    psp = doc.page_setup("Layout1", fmt="ISO A0")
    assert len(psp.query("POINT")) == 1


def test_new_layout2():
    doc = ezdxf.new()
    assert len(doc.layouts) == 2
    psp = doc.page_setup("Layout2", fmt="ISO A0")
    assert len(doc.layouts) == 3
    assert psp.dxf_layout.dxf.paper_width == 1189
    assert psp.dxf_layout.dxf.paper_height == 841


if __name__ == '__main__':
    pytest.main([__file__])
