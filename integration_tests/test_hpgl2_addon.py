#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
from pathlib import Path
from xml.etree import ElementTree as ET
from ezdxf.addons.hpgl2 import api as hpgl2

DATA = Path(__file__).parent / "data"
PLOTFILE = DATA / "PLOTFILE.plt"

if not PLOTFILE.exists():
    pytest.skip(reason=f"required file '{PLOTFILE}' not found", allow_module_level=True)


@pytest.fixture(scope="module")
def svg_str():
    data = PLOTFILE.read_bytes()
    return hpgl2.to_svg(data)


def test_svg_was_created(svg_str):
    assert len(svg_str) > 70000


def test_basic_svg_attributes(svg_str):
    root = ET.fromstring(svg_str)
    assert root.tag.endswith("svg")
    assert root.attrib["width"] == "593.8mm"
    assert root.attrib["height"] == "419.9mm"
    assert root.attrib["viewBox"] == "0 0 23752 16794"


if __name__ == '__main__':
    pytest.main([__file__])
