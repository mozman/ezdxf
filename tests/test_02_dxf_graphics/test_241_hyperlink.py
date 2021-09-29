# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.entities import DXFGraphic


def test_set_hyperlink():
    entity = DXFGraphic()
    assert entity.has_hyperlink() is False
    entity.set_hyperlink("link")
    assert entity.has_hyperlink() is True
    hyperlink, description, location = entity.get_hyperlink()
    assert hyperlink == "link"
    assert description == ""
    assert location == ""


def test_set_description():
    entity = DXFGraphic()
    entity.set_hyperlink("link", "description")
    hyperlink, description, location = entity.get_hyperlink()
    assert hyperlink == "link"
    assert description == "description"
    assert location == ""


def test_set_location():
    entity = DXFGraphic()
    entity.set_hyperlink("link", "description", "location")
    hyperlink, description, location = entity.get_hyperlink()
    assert hyperlink == "link"
    assert description == "description"
    assert location == "location"


if __name__ == "__main__":
    pytest.main([__file__])
