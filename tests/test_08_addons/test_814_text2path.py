#  Copyright (c) 2021-2023, Manfred Moitzi
#  License: MIT License

import pytest
import platform

if platform.system() != "Windows":
    pytest.skip(
        reason="works for some reasons only on Windows", allow_module_level=True
    )
# These test do not work on my Linux Mint system.
# The test file fails when started as a whole session, but passes if I start
# failing test classes individually by the PyCharm debugger.
# The problem is the font_manager:
# When started as single test class or in debugger mode the repo fonts are loaded as it
# should be. Started as normal session the system fonts are loaded, which shouldn't be
# possible - I guess there is some pytest magic happening in the background which messes
# things up.
# On Windows everything works fine, so the module works as expected.

from ezdxf.tools.font_face import FontFace
from ezdxf.addons import text2path
from ezdxf.path import Path
from ezdxf import path, bbox
from ezdxf.entities import Text, Hatch
from ezdxf.layouts import VirtualLayout
from ezdxf.enums import TextEntityAlignment

# always available in common test scenarios:
DEFAULT = "LiberationSans-Regular.ttf"
NOTO_SANS_SC = "NotoSansSC-Regular.otf"


def _to_paths(s, f=DEFAULT):
    return text2path.make_paths_from_str(s, font=FontFace(ttf=f))


# Font 'Arial' required, a replacement fonts may return a different
# path/hole configuration! issue #515
CHAR_TO_PATH = [
    ["1", 1],
    ["2", 1],
    [".", 1],
    ["0", 2],
    ["a", 2],
    ["!", 2],
    ["@", 2],
    ["8", 3],
    ["ü", 3],
    ["&", 3],
    ["ä", 4],
    ["ö", 4],
    ["%", 5],
]


@pytest.mark.parametrize("s,c", CHAR_TO_PATH)
def test_make_paths_from_str(s: str, c: int):
    # change of assertion from == to >= is based on an error on RPi & Ubuntu
    # Server 21.10 & matplotlib
    # assert len(_to_paths("ü")) == 4  instead of 3
    # Do not test how matplotlib works here, the only important fact is:
    # do we get path objects
    assert len(_to_paths(s)) >= c


@pytest.mark.parametrize("s,c", [["中", 3], ["国", 4], ["文", 3], ["字", 2]])
def test_chinese_char_paths_from_str(s, c):
    assert len(_to_paths(s, f=NOTO_SANS_SC)) == c


def contour_and_holes(group):
    return group[0], group[1:]


@pytest.mark.parametrize(
    "s,h",
    [
        ["1", 0],
        ["2", 0],
        [".", 0],
        ["0", 1],
        ["a", 1],
        ["8", 2],
    ],
)
def test_group_one_contour_with_holes(s, h):
    paths = _to_paths(s)
    result = list(path.group_paths(paths))
    contour, holes = contour_and_holes(result[0])
    assert isinstance(contour, Path)
    assert len(holes) == h


@pytest.mark.parametrize("s", [":", "!", ";", "="])
def test_group_two_contours_without_holes(s):
    paths = _to_paths(s)
    result = list(path.group_paths(paths))
    assert len(result) == 2
    contour, holes = contour_and_holes(result[0])
    assert isinstance(contour, Path)
    assert len(holes) == 0


@pytest.mark.parametrize(
    "s",
    [
        "Ü",
        "ö",
        "ä",
    ],
)
def test_group_three_contours_and_ignore_holes(s):
    paths = _to_paths(s)
    result = list(path.group_paths(paths))
    assert len(result) == 3
    contour, holes = contour_and_holes(result[0])
    assert isinstance(contour, Path)


@pytest.mark.parametrize("s,c", [["中", 1], ["国", 1], ["文", 2], ["字", 2]])
def test_group_chinese_chars_and_ignore_holes(s, c):
    paths = _to_paths(s, f=NOTO_SANS_SC)
    result = list(path.group_paths(paths))
    assert len(result) == c
    contour, holes = contour_and_holes(result[0])
    assert isinstance(contour, Path)


@pytest.fixture(scope="module")
def ff():
    return FontFace(family=DEFAULT)


class TestMakePathFromString:
    # Surprise - even 0 and negative values work without any exceptions!
    @pytest.mark.parametrize("size", [0, 0.05, 1, 2, 100, -1, -2, -100])
    def test_text_path_height_for_exact_drawing_units(self, size, ff):
        paths = text2path.make_paths_from_str("X", font=ff, size=size)
        bbox = path.bbox(paths)
        assert bbox.size.y == pytest.approx(abs(size))

    @pytest.mark.parametrize("size", [0.05, 1, 2, 100])
    def test_path_coordinates_for_positive_size(self, size, ff):
        paths = text2path.make_paths_from_str("X", font=ff, size=size)
        bbox = path.bbox(paths)
        assert bbox.extmax.y == pytest.approx(size)
        assert bbox.extmin.y == pytest.approx(0)

    @pytest.mark.parametrize("size", [-0.05, -1, -2, -100])
    def test_path_coordinates_for_negative_size(self, size, ff):
        # Negative text height mirrors text about the x-axis!
        paths = text2path.make_paths_from_str("X", font=ff, size=size)
        bbox = path.bbox(paths)
        assert bbox.extmax.y == pytest.approx(0)
        assert bbox.extmin.y == pytest.approx(size)

    @pytest.mark.parametrize("size", [0.05, 1, 2, 100])
    def test_length_for_fit_alignment(self, size, ff):
        length = 3
        paths = text2path.make_paths_from_str(
            "XXX",
            font=ff,
            size=size,
            align=TextEntityAlignment.FIT,
            length=length,
        )
        bbox = path.bbox(paths)
        assert bbox.size.x == pytest.approx(length), "expect exact length"
        assert bbox.size.y == pytest.approx(size), "text height should be unscaled"

    @pytest.mark.parametrize("size", [0.05, 1, 2, 100])
    def test_scaled_height_and_length_for_aligned_text(self, size, ff):
        length = 3
        paths = text2path.make_paths_from_str(
            "XXX", font=ff, size=size, align=TextEntityAlignment.LEFT
        )
        default = path.bbox(paths)
        paths = text2path.make_paths_from_str(
            "XXX",
            font=ff,
            size=size,
            align=TextEntityAlignment.ALIGNED,
            length=length,
        )
        bbox = path.bbox(paths)
        scale = bbox.size.x / default.size.x
        assert bbox.size.x == pytest.approx(length), "expect exact length"
        assert bbox.size.y == pytest.approx(
            size * scale
        ), "text height should be scaled"

    def test_paths_from_empty_string(self, ff):
        paths = text2path.make_paths_from_str("", font=ff)
        assert len(paths) == 0

    def test_make_multi_path_object(self, ff):
        p = text2path.make_path_from_str("ABC", font=ff)
        assert p.has_sub_paths is True
        assert len(list(p.sub_paths())) == 6

    def test_make_empty_multi_path_object(self, ff):
        p = text2path.make_path_from_str("", font=ff)
        assert p.has_sub_paths is False
        assert len(p) == 0


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
            "XXX", font=ff, align=TextEntityAlignment.FIT, length=length
        )
        paths = []
        for hatch in hatches:
            paths.extend(path.from_hatch(hatch))
        bbox = path.bbox(paths)
        assert bbox.size.x == pytest.approx(length), "expect exact length"
        assert bbox.size.y == pytest.approx(1.0), "text height should be unscaled"


def test_check_entity_type():
    with pytest.raises(TypeError):
        text2path.check_entity_type(None)
    with pytest.raises(TypeError):
        text2path.check_entity_type(Hatch())


def make_text(text, location, alignment, height=1.0, rotation=0):
    text = Text.new(
        dxfattribs={
            "text": text,
            "height": height,
            "rotation": rotation,
        }
    )
    text.set_placement(location, align=alignment)
    return text


def get_path_bbox(text):
    p = text2path.make_path_from_entity(text)
    return path.bbox([p], fast=True)


def get_paths_bbox(text):
    paths = text2path.make_paths_from_entity(text)
    return path.bbox(paths, fast=True)


def get_hatches_bbox(text):
    hatches = text2path.make_hatches_from_entity(text)
    return bbox.extents(hatches, fast=True)


@pytest.fixture(params=[get_path_bbox, get_paths_bbox, get_hatches_bbox])
def get_bbox(request):
    return request.param


class TestMakePathsFromEntity:
    """Test Paths (and Hatches) from TEXT entities.

    make_hatches_from_entity() is basically make_paths_from_entity(), but
    returns Hatch entities instead of Path objects.

    Important: Don't use text with top or bottom curves for testing ("S", "O").
    The Path bounding box calculation uses the "fast" method by checking only
    the curve control points, which are outside the curve borders.

    """

    @pytest.mark.parametrize(
        "builder, type_",
        [
            (text2path.make_paths_from_entity, Path),
            (text2path.make_hatches_from_entity, Hatch),
        ],
    )
    def test_text_returns_correct_types(self, builder, type_):
        text = make_text("TEXT", (0, 0), TextEntityAlignment.LEFT)
        objects = builder(text)
        assert len(objects) == 4
        assert isinstance(objects[0], type_)

    def test_text_height(self, get_bbox):
        text = make_text("TEXT", (0, 0), TextEntityAlignment.LEFT, height=1.5)
        bbox = get_bbox(text)
        assert bbox.size.y == pytest.approx(1.5)

    def test_alignment_left(self, get_bbox):
        text = make_text("TEXT", (7, 7), TextEntityAlignment.LEFT)
        bbox = get_bbox(text)
        # font rendering is tricky, base offsets depend on the rendering engine
        # and on extended font metrics, ...
        assert bbox.extmin.x == pytest.approx(7, abs=0.1)

    def test_alignment_center(self, get_bbox):
        text = make_text("TEXT", (7, 7), TextEntityAlignment.CENTER)
        bbox = get_bbox(text)
        assert bbox.center.x == pytest.approx(7)

    def test_alignment_right(self, get_bbox):
        text = make_text("TEXT", (7, 7), TextEntityAlignment.RIGHT)
        bbox = get_bbox(text)
        assert bbox.extmax.x == pytest.approx(7)

    def test_alignment_baseline(self, get_bbox):
        text = make_text("TEXT", (7, 7), TextEntityAlignment.CENTER)
        bbox = get_bbox(text)
        assert bbox.extmin.y == pytest.approx(7)

    def test_alignment_bottom(self, get_bbox):
        text = make_text("j", (7, 7), TextEntityAlignment.BOTTOM_CENTER)
        bbox = get_bbox(text)
        # bottom border of descender should be 7, but ...
        assert bbox.extmin.y == pytest.approx(7, abs=0.1)

    def test_alignment_middle(self, get_bbox):
        text = make_text("X", (7, 7), TextEntityAlignment.MIDDLE_CENTER)
        bbox = get_bbox(text)
        assert bbox.center.y == pytest.approx(7)

    def test_alignment_top(self, get_bbox):
        text = make_text("X", (7, 7), TextEntityAlignment.TOP_CENTER)
        bbox = get_bbox(text)
        assert bbox.extmax.y == pytest.approx(7)

    def test_alignment_fit(self, get_bbox):
        length = 2
        height = 1
        text = make_text("TEXT", (0, 0), TextEntityAlignment.LEFT, height=height)
        text.set_placement((1, 0), (1 + length, 0), TextEntityAlignment.FIT)
        bbox = get_bbox(text)
        assert bbox.size.x == length, "expected text length fits into given length"
        assert bbox.size.y == pytest.approx(height), "expected unscaled text height"
        assert bbox.extmin.isclose((1, 0))

    def test_alignment_aligned(self, get_bbox):
        length = 2
        height = 1
        text = make_text("TEXT", (0, 0), TextEntityAlignment.CENTER, height=height)
        bbox = get_bbox(text)
        ratio = bbox.size.x / bbox.size.y

        text.set_placement((1, 0), (1 + length, 0), TextEntityAlignment.ALIGNED)
        bbox = get_bbox(text)

        assert bbox.size.x == length, "expected text length fits into given length"
        assert bbox.size.y != height, "expected scaled text height"
        assert bbox.extmin.isclose((1, 0))
        assert bbox.size.x / bbox.size.y == pytest.approx(
            ratio
        ), "expected same width/height ratio"

    def test_rotation_90(self, get_bbox):
        # Horizontal reference measurements:
        bbox_hor = get_bbox(
            make_text("TEXT", (7, 7), TextEntityAlignment.MIDDLE_CENTER)
        )

        text_vert = make_text(
            "TEXT", (7, 7), TextEntityAlignment.MIDDLE_CENTER, rotation=90
        )
        bbox_vert = get_bbox(text_vert)
        assert bbox_hor.center == bbox_vert.center
        assert bbox_hor.size.x == bbox_vert.size.y
        assert bbox_hor.size.y == bbox_vert.size.x


Kind = text2path.Kind


class TestVirtualEntities:
    @pytest.fixture
    def text(self):
        return make_text("TEST", (0, 0), TextEntityAlignment.LEFT)

    def test_virtual_entities_as_hatches(self, text):
        entities = text2path.virtual_entities(text, kind=Kind.HATCHES)
        types = {e.dxftype() for e in entities}
        assert types == {"HATCH"}

    def test_virtual_entities_as_splines_and_polylines(self, text):
        entities = text2path.virtual_entities(text, kind=Kind.SPLINES)
        types = {e.dxftype() for e in entities}
        assert types == {"SPLINE", "POLYLINE"}

    def test_virtual_entities_as_lwpolylines(self, text):
        entities = text2path.virtual_entities(text, kind=Kind.LWPOLYLINES)
        types = {e.dxftype() for e in entities}
        assert types == {"LWPOLYLINE"}

    def test_virtual_entities_to_all_types_at_once(self, text):
        entities = text2path.virtual_entities(
            text, kind=Kind.HATCHES + Kind.SPLINES + Kind.LWPOLYLINES
        )
        types = {e.dxftype() for e in entities}
        assert types == {"LWPOLYLINE", "SPLINE", "POLYLINE", "HATCH"}


class TestExplode:
    """Based on text2path.virtual_entities() function, see test above."""

    @pytest.fixture
    def text(self):
        return make_text("TEST", (0, 0), TextEntityAlignment.LEFT)

    def test_source_entity_is_destroyed(self, text):
        assert text.is_alive is True
        text2path.explode(text, kind=4)
        assert text.is_alive is False, "source entity should always be destroyed"

    def test_explode_entity_into_layout(self, text):
        layout = VirtualLayout()
        entities = text2path.explode(text, kind=Kind.LWPOLYLINES, target=layout)
        assert len(entities) == len(
            layout
        ), "expected all entities added to the target layout"

    def test_explode_entity_into_the_void(self, text):
        assert text.get_layout() is None, "source entity should not have a layout"
        entities = text2path.explode(text, kind=Kind.LWPOLYLINES, target=None)
        assert len(entities) == 4, "explode should work without a target layout"


if __name__ == "__main__":
    pytest.main([__file__])
