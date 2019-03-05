# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def tables():
    doc = ezdxf.new2()
    return doc.tables


def test_constructor(tables):
    assert tables.layers is not None
    assert tables.linetypes is not None
    assert tables.appids is not None
    assert tables.styles is not None
    assert tables.dimstyles is not None
    assert tables.views is not None
    assert tables.viewports is not None
    assert tables.ucs is not None
    assert tables.block_records is not None


def test_getattr_upper_case(tables):
    with pytest.raises(AttributeError):
        _ = tables.LINETYPES


def test_error_getattr(tables):
    with pytest.raises(AttributeError):
        _ = tables.test
