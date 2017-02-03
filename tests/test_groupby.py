import pytest
import ezdxf

from ezdxf.groupby import groupby


def modelspace():
    dwg = ezdxf.new('AC1009')
    msp = dwg.modelspace()
    msp.add_line((0, 0), (10, 0), {'layer': 'lay_lines', 'color': 7})
    msp.add_polyline2d([(0, 0), (3, 1), (7, 4), (10, 0)], {'layer': 'lay_lines', 'color': 6})
    msp.add_text("TEST", dxfattribs={'layer': 'lay_text', 'color': 6})
    msp.add_text("TEST2", dxfattribs={'layer': 'lay_text2', 'color': 6})
    # just 3 entities: LINE, TEXT, POLYLINE - VERTEX & SEQEND now linked to the POLYLINE entity, and do not appear
    # in any entity space
    return msp

MODEL_SPACE = modelspace()


def test_groupby_dxfattrib():
    result = groupby(MODEL_SPACE, dxfattrib='layer')
    assert len(result) == 3  # 3 different layers
    assert set(result.keys()) == {'lay_lines', 'lay_text', 'lay_text2'}


def test_groupby_not_existing_dxfattrib():
    result = groupby(MODEL_SPACE, dxfattrib='xxx')
    # no result, but does not raise an error, this is necessary, because otherwise, only DXF attributes supported by ALL
    # entities could be used, this implementation just ignores DXF entities which do not support the specified
    # dxfattrib, side effect: you can specify anything in dxfattrib.
    assert len(result) == 0


def test_groupby_key():
    result = groupby(MODEL_SPACE, key=lambda e: (e.dxf.color, e.dxf.layer))
    assert len(result) == 4  # 4 different (color, layers) combinations
    assert set(result.keys()) == {(6, 'lay_lines'), (7, 'lay_lines'), (6, 'lay_text'), (6, 'lay_text2')}


def test_groupby_result():
    result = groupby(MODEL_SPACE, dxfattrib='layer')
    lines = result['lay_lines']
    assert len(lines) == 2

    text = result['lay_text']
    assert len(text) == 1

    with pytest.raises(KeyError):
        e = result['mozman']


def test_calling_convention():
    with pytest.raises(ValueError):  # if both query arguments are set
        groupby([], dxfattrib='layer', key=lambda e: e.dxf.layer)

    with pytest.raises(ValueError):  # if no query argument is set
        groupby([])

if __name__ == '__main__':
    pytest.main([__file__])

