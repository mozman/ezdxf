#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf

MAX_HANDLE = 1000


@pytest.fixture
def doc():
    mydoc = ezdxf.new()
    msp = mydoc.modelspace()
    for _ in range(100):
        msp.add_point((0, 0))
    return mydoc


def test_unset_redraw_order_returns_empty_tuple(doc):
    msp = doc.modelspace()
    assert msp.get_redraw_order() == tuple()


def to_handle(value: int) -> str:
    return f"{value:X}"


def get_order(msp):
    return {
        e.dxf.handle: to_handle(sort_handle)
        for (e, sort_handle) in zip(msp, range(MAX_HANDLE, 0, -1))
    }


def set_redraw_order(msp):
    msp.set_redraw_order(get_order(msp))


def test_set_redraw_order(doc):
    msp = doc.modelspace()
    set_redraw_order(msp)
    result = list(msp.get_redraw_order())

    assert len(result) == len(
        msp
    ), "redraw entry count does not match entity count"

    assert set(k for k, v in result) == set(
        e.dxf.handle for e in msp
    ), "missing source handles"

    expected_order = get_order(msp)
    assert set(result) == set(
        expected_order.items()
    ), "redraw order does not match source document"


def test_store_and_load_redraw_order(doc, tmp_path):
    p = tmp_path / "set_redraw_order.dxf"
    set_redraw_order(doc.modelspace())
    doc.saveas(p)
    src_msp = doc.modelspace()

    fs_copy = ezdxf.readfile(p)
    result = list(fs_copy.modelspace().get_redraw_order())

    assert len(result) == len(
        src_msp
    ), "redraw entry count does not match entity count"

    assert set(k for k, v in result) == set(
        e.dxf.handle for e in src_msp
    ), "missing source handles"

    expected_order = get_order(src_msp)
    assert set(result) == set(
        expected_order.items()
    ), "redraw order does not match source document"


if __name__ == "__main__":
    pytest.main([__file__])
