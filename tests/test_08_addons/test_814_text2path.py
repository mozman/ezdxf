#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest

pytest.importorskip('matplotlib')  # requires matplotlib!
from matplotlib.font_manager import FontProperties, findfont

NOTO_SANS_SC = 'Noto Sans SC'
noto_sans_sc_not_found = 'Noto' not in findfont(
    FontProperties(family=NOTO_SANS_SC))

from ezdxf.tools.fonts import FontFace
from ezdxf.addons import text2path
from ezdxf.path import Path
from ezdxf import path


def _to_paths(s, f='Arial'):
    return text2path.make_paths_from_str(s, font=FontFace(family=f))


@pytest.mark.parametrize('s,c', [
    ['1', 1], ['2', 1], ['.', 1],
    ['0', 2], ['a', 2], ['!', 2], ['@', 2],
    ['8', 3], ['ü', 3], ['&', 3],
    ['ä', 4], ['ö', 4],
    ['%', 5],
])
def test_make_paths_from_str(s, c):
    assert len(_to_paths(s)) == c


@pytest.mark.skipif(noto_sans_sc_not_found,
                    reason=f'Font "{NOTO_SANS_SC}" not found')
@pytest.mark.parametrize('s,c', [
    ["中", 3], ["国", 4], ["文", 3], ["字", 2]
])
def test_chinese_char_paths_from_str(s, c):
    assert len(_to_paths(s, f=NOTO_SANS_SC)) == c


@pytest.mark.parametrize('s,h', [
    ['1', 0], ['2', 0], ['.', 0], ['0', 1], ['a', 1], ['8', 2],
])
def test_group_one_contour_with_holes(s, h):
    paths = _to_paths(s)
    result = list(text2path.group_contour_and_holes(paths))
    assert len(result) == 1
    contour, holes = result[0]
    assert isinstance(contour, Path)
    assert isinstance(holes, list)
    assert len(holes) == h


@pytest.mark.parametrize('s', [':', '!', ';', '='])
def test_group_two_contours_without_holes(s):
    paths = _to_paths(s)
    result = list(text2path.group_contour_and_holes(paths))
    assert len(result) == 2
    contour, holes = result[0]
    assert isinstance(contour, Path)
    assert len(holes) == 0


@pytest.mark.parametrize('s', ['Ü', 'ö', 'ä', ])
def test_group_three_contours_and_ignore_holes(s):
    paths = _to_paths(s)
    result = list(text2path.group_contour_and_holes(paths))
    assert len(result) == 3
    contour, holes = result[0]
    assert isinstance(contour, Path)


def test_group_percent_sign():
    # Special case %: lower o is inside of the slash bounding box, but HATCH
    # creation works as expected!
    paths = _to_paths('%')
    result = list(text2path.group_contour_and_holes(paths))
    assert len(result) == 2
    contour, holes = result[0]
    assert isinstance(contour, Path)
    assert len(holes) == 2


@pytest.mark.skipif(noto_sans_sc_not_found,
                    reason='Font "Noto Sans SC" not found')
@pytest.mark.parametrize('s,c', [
    ["中", 1], ["国", 1], ["文", 2], ["字", 2]
])
def test_group_chinese_chars_and_ignore_holes(s, c):
    paths = _to_paths(s, f=NOTO_SANS_SC)
    result = list(text2path.group_contour_and_holes(paths))
    assert len(result) == c
    contour, holes = result[0]
    assert isinstance(contour, Path)


class TestStringToPathMetrics:
    @pytest.fixture(scope='class')
    def ff(self):
        return FontFace(family="Arial")

    # Surprise - even 0 and negative values work without any exceptions!
    @pytest.mark.parametrize('size', [0, 0.05, 1, 2, 100, -1, -2, -100])
    def test_text_path_height_for_exact_drawing_units(self, size, ff):
        paths = text2path.make_paths_from_str("X", font=ff, size=size)
        bbox = path.bbox(paths)
        assert bbox.size.y == pytest.approx(abs(size))

    @pytest.mark.parametrize('size', [0.05, 1, 2, 100])
    def test_path_coordinates_for_positive_size(self, size, ff):
        paths = text2path.make_paths_from_str("X", font=ff, size=size)
        bbox = path.bbox(paths)
        assert bbox.extmax.y == pytest.approx(size)
        assert bbox.extmin.y == pytest.approx(0)

    @pytest.mark.parametrize('size', [-0.05, -1, -2, -100])
    def test_path_coordinates_for_negative_size(self, size, ff):
        # Negative text height mirrors text about the x-axis!
        paths = text2path.make_paths_from_str("X", font=ff, size=size)
        bbox = path.bbox(paths)
        assert bbox.extmax.y == pytest.approx(0)
        assert bbox.extmin.y == pytest.approx(size)

    @pytest.mark.parametrize('size', [0.05, 1, 2, 100])
    def test_length_for_fit_alignment(self, size, ff):
        length = 3
        paths = text2path.make_paths_from_str(
            "XXX", font=ff, size=size, align="FIT", length=length)
        bbox = path.bbox(paths)
        assert bbox.size.x == pytest.approx(length), "expect exact length"
        assert bbox.size.y == pytest.approx(size), \
            "text height should be unscaled"

    @pytest.mark.parametrize('size', [0.05, 1, 2, 100])
    def test_scaled_height_and_length_for_aligned_text(self, size, ff):
        length = 3
        paths = text2path.make_paths_from_str("XXX", font=ff, size=size,
                                              align="LEFT")
        default = path.bbox(paths)
        paths = text2path.make_paths_from_str(
            "XXX", font=ff, size=size, align="ALIGNED", length=length)
        bbox = path.bbox(paths)
        scale = bbox.size.x / default.size.x
        assert bbox.size.x == pytest.approx(length), "expect exact length"
        assert bbox.size.y == pytest.approx(size * scale), \
            "text height should be scaled"


if __name__ == '__main__':
    pytest.main([__file__])
