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
from ezdxf import path, bbox
from ezdxf.entities import Text, Hatch


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


def contour_and_holes(group):
    return group[0], group[1:]


@pytest.mark.parametrize('s,h', [
    ['1', 0], ['2', 0], ['.', 0], ['0', 1], ['a', 1], ['8', 2],
])
def test_group_one_contour_with_holes(s, h):
    paths = _to_paths(s)
    result = list(path.group_paths(paths))
    contour, holes = contour_and_holes(result[0])
    assert isinstance(contour, Path)
    assert len(holes) == h


@pytest.mark.parametrize('s', [':', '!', ';', '='])
def test_group_two_contours_without_holes(s):
    paths = _to_paths(s)
    result = list(path.group_paths(paths))
    assert len(result) == 2
    contour, holes = contour_and_holes(result[0])
    assert isinstance(contour, Path)
    assert len(holes) == 0


@pytest.mark.parametrize('s', ['Ü', 'ö', 'ä', ])
def test_group_three_contours_and_ignore_holes(s):
    paths = _to_paths(s)
    result = list(path.group_paths(paths))
    assert len(result) == 3
    contour, holes = contour_and_holes(result[0])
    assert isinstance(contour, Path)


def test_group_percent_sign():
    # Special case %: lower o is inside of the slash bounding box, but HATCH
    # creation works as expected!
    paths = _to_paths('%')
    result = list(path.group_paths(paths))
    assert len(result) == 2
    contour, holes = contour_and_holes(result[0])
    assert isinstance(contour, Path)
    assert len(holes) == 2


@pytest.mark.skipif(noto_sans_sc_not_found,
                    reason='Font "Noto Sans SC" not found')
@pytest.mark.parametrize('s,c', [
    ["中", 1], ["国", 1], ["文", 2], ["字", 2]
])
def test_group_chinese_chars_and_ignore_holes(s, c):
    paths = _to_paths(s, f=NOTO_SANS_SC)
    result = list(path.group_paths(paths))
    assert len(result) == c
    contour, holes = contour_and_holes(result[0])
    assert isinstance(contour, Path)


@pytest.fixture(scope='module')
def ff():
    return FontFace(family="Arial")


class TestMakePathFromString:
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

    def test_paths_from_empty_string(self, ff):
        paths = text2path.make_paths_from_str("", font=ff)
        assert len(paths) == 0


class TestMakeHatchesFromString:
    def test_hatches_from_empty_string(self, ff):
        hatches = text2path.make_hatches_from_str("", font=ff)
        assert len(hatches) == 0

    def test_make_exterior_only_hatches(self, ff):
        hatches = text2path.make_hatches_from_str("XXX", font=ff)
        assert len(hatches) == 3
        assert len(hatches[0].paths) == 1

    def test_make_hatches_with_holes(self, ff):
        hatches = text2path.make_hatches_from_str("AAA", font=ff)
        assert len(hatches) == 3
        assert len(hatches[0].paths) == 2, "expected external and one hole"

    def test_total_length_for_fit_alignment(self, ff):
        length = 3
        hatches = text2path.make_hatches_from_str(
            "XXX", font=ff, align="FIT", length=length)
        paths = []
        for hatch in hatches:
            paths.extend(path.from_hatch(hatch))
        bbox = path.bbox(paths)
        assert bbox.size.x == pytest.approx(length), "expect exact length"
        assert bbox.size.y == pytest.approx(1.0), \
            "text height should be unscaled"


def make_text(text, location, alignment, height=1.0, rotation=0):
    text = Text.new(dxfattribs={
        'text': text,
        'height': height,
        'rotation': rotation,
    })
    text.set_pos(location, align=alignment)
    return text


def get_path_bbox(text):
    paths = text2path.make_paths_from_entity(text)
    return path.bbox(paths, flatten=False)


def get_hatches_bbox(text):
    hatches = text2path.make_hatches_from_entity(text)
    return bbox.extents(hatches, flatten=False)


@pytest.fixture(params=[get_path_bbox, get_hatches_bbox])
def get_bbox(request):
    return request.param


class TestMakePathsFromEntity:
    """ Test Paths (and Hatches) from TEXT entities.

    make_hatches_from_entity() is basically make_paths_from_entity(), but
    returns Hatch entities instead of Path objects.

    Important: Don't use text with top or bottom curves for testing ("S", "O").
    The Path bounding box calculation uses the "fast" method by checking only
    the curve control points, which are outside the curve borders.

    """

    @pytest.mark.parametrize("builder, type_", [
        (text2path.make_paths_from_entity, Path),
        (text2path.make_hatches_from_entity, Hatch),
    ])
    def test_text_returns_correct_types(self, builder, type_):
        text = make_text("TEXT", (0, 0), 'LEFT')
        objects = builder(text)
        assert len(objects) == 4
        assert isinstance(objects[0], type_)

    def test_text_height(self, get_bbox):
        text = make_text("TEXT", (0, 0), 'LEFT', height=1.5)
        bbox = get_bbox(text)
        assert bbox.size.y == pytest.approx(1.5)

    def test_alignment_left(self, get_bbox):
        text = make_text("TEXT", (7, 7), 'LEFT')
        bbox = get_bbox(text)
        # font rendering is tricky, base offsets depend on the rendering engine
        # and on extended font metrics, ...
        assert bbox.extmin.x == pytest.approx(7, abs=0.1)

    def test_alignment_center(self, get_bbox):
        text = make_text("TEXT", (7, 7), 'CENTER')
        bbox = get_bbox(text)
        assert bbox.center.x == pytest.approx(7)

    def test_alignment_right(self, get_bbox):
        text = make_text("TEXT", (7, 7), 'RIGHT')
        bbox = get_bbox(text)
        assert bbox.extmax.x == pytest.approx(7)

    def test_alignment_baseline(self, get_bbox):
        text = make_text("TEXT", (7, 7), 'CENTER')
        bbox = get_bbox(text)
        assert bbox.extmin.y == pytest.approx(7)

    def test_alignment_bottom(self, get_bbox):
        text = make_text("j", (7, 7), 'BOTTOM_CENTER')
        bbox = get_bbox(text)
        # bottom border of descender should be 7, but ...
        assert bbox.extmin.y == pytest.approx(7, abs=0.1)

    def test_alignment_middle(self, get_bbox):
        text = make_text("X", (7, 7), 'MIDDLE_CENTER')
        bbox = get_bbox(text)
        assert bbox.center.y == pytest.approx(7)

    def test_alignment_top(self, get_bbox):
        text = make_text("X", (7, 7), 'TOP_CENTER')
        bbox = get_bbox(text)
        assert bbox.extmax.y == pytest.approx(7)

    def test_alignment_fit(self, get_bbox):
        length = 2
        height = 1
        text = make_text("TEXT", (0, 0), 'LEFT', height=height)
        text.set_pos((1, 0), (1 + length, 0), 'FIT')
        bbox = get_bbox(text)
        assert bbox.size.x == length, "expected text length fits into given length"
        assert bbox.size.y == height, "expected unscaled text height"
        assert bbox.extmin == (1, 0)

    def test_alignment_aligned(self, get_bbox):
        length = 2
        height = 1
        text = make_text("TEXT", (0, 0), 'CENTER', height=height)
        bbox = get_bbox(text)
        ratio = bbox.size.x / bbox.size.y

        text.set_pos((1, 0), (1 + length, 0), 'ALIGNED')
        bbox = get_bbox(text)

        assert bbox.size.x == length, "expected text length fits into given length"
        assert bbox.size.y != height, "expected scaled text height"
        assert bbox.extmin == (1, 0)
        assert bbox.size.x / bbox.size.y == pytest.approx(ratio), \
            "expected same width/height ratio"

    def test_rotation_90(self, get_bbox):
        # Horizontal reference measurements:
        bbox_hor = get_bbox(make_text("TEXT", (7, 7), 'MIDDLE_CENTER'))

        text_vert = make_text("TEXT", (7, 7), 'MIDDLE_CENTER', rotation=90)
        bbox_vert = get_bbox(text_vert)
        assert bbox_hor.center == bbox_vert.center
        assert bbox_hor.size.x == bbox_vert.size.y
        assert bbox_hor.size.y == bbox_vert.size.x


class TestExplode:
    pass


if __name__ == '__main__':
    pytest.main([__file__])
