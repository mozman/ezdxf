from ezdxf.addons.drawing.frontend import _is_visible
from ezdxf.entities import Point


def test_is_visible():
    entity = Point()

    entity.dxf.set('layer', '0')  # 0 => visibility tied to the inserted layer
    assert not _is_visible(entity, set(), '0')
    assert not _is_visible(entity, set(), '1')

    assert _is_visible(entity, {'0'}, '0')
    assert not _is_visible(entity, {'0'}, '1')
    assert not _is_visible(entity, {'1'}, '0')
    assert _is_visible(entity, {'1'}, '1')

    entity.dxf.set('layer', '1')  # !0 => visibility tied to that layer
    assert not _is_visible(entity, set(), '0')
    assert not _is_visible(entity, set(), '1')

    assert not _is_visible(entity, {'0'}, '0')
    assert not _is_visible(entity, {'0'}, '1')
    assert _is_visible(entity, {'1'}, '0')
    assert _is_visible(entity, {'1'}, '1')
