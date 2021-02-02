#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Union, List, Dict, Iterable, Tuple
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties, findfont

from ezdxf.entities import Text, Attrib, Hatch
from ezdxf.lldxf import const
from ezdxf.math import Matrix44, BoundingBox
from ezdxf.render import path, nesting, Path
from ezdxf.tools import text, fonts

AnyText = Union[Text, Attrib]


def make_paths_from_str(s: str,
                        font: fonts.FontFace,
                        halign: int = const.LEFT,
                        valign: int = const.BASELINE,
                        m: Matrix44 = None) -> List[Path]:
    """ Convert a single line string `s` into a list of
    :class:`~ezdxf.render.path.Path` objects. All paths are returned in a single
    list. The path objects are created for the text height of one drawing unit
    as cap height (height of uppercase letter "X") and the insertion point is
    (0, 0).
    The paths  are aligned to this insertion point.
    BASELINE means the bottom of the letter "X".

    Args:
         s: text to convert
         font: font face definition
         halign: horizontal alignment: LEFT=0, CENTER=1, RIGHT=2
         valign: vertical alignment: BASELINE=0, BOTTOM=1, MIDDLE=2, TOP=3
         m: transformation :class:`~ezdxf.math.Matrix44`

    """
    font_properties, font_measurements = _get_font_data(font)
    paths = _str_to_paths(s, font_properties)
    bbox = path.bbox(paths, precise=False)
    matrix = get_alignment_transformation(
        font_measurements, bbox, halign, valign)
    if m is not None:
        matrix *= m
    return list(path.transform_paths(paths, matrix))


def _get_font_data(
        font: fonts.FontFace) -> Tuple[FontProperties, fonts.FontMeasurements]:
    fp = FontProperties(
        family=font.family,
        style=font.style,
        stretch=font.stretch,
        weight=font.weight,
    )
    ttf_path = findfont(fp)
    fonts.load()  # not expensive if already loaded
    # The ttf file path is the cache key for font measurements:
    fm = fonts.get_font_measurements(ttf_path)
    return fp, fm


def _str_to_paths(s: str, fp: FontProperties) -> List[Path]:
    text_path = TextPath((0, 0), s, size=1, prop=fp, usetex=False)
    return list(path.from_matplotlib_path(text_path))


def get_alignment_transformation(fm: fonts.FontMeasurements, bbox: BoundingBox,
                                 halign: int, valign: int) -> Matrix44:
    if halign == const.LEFT:
        shift_x = 0
    elif halign == const.RIGHT:
        shift_x = -bbox.extmax.x
    elif halign == const.CENTER:
        shift_x = -bbox.center.x
    else:
        raise ValueError(f'invalid halign argument: {halign}')
    cap_height = max(fm.cap_height, bbox.extmax.y)
    descender_height = max(fm.descender_height, abs(bbox.extmin.y))
    if valign == const.BASELINE:
        shift_y = 0
    elif valign == const.TOP:
        shift_y = -cap_height
    elif valign == const.MIDDLE:
        shift_y = -cap_height / 2
    elif valign == const.BOTTOM:
        shift_y = descender_height
    else:
        raise ValueError(f'invalid valign argument: {valign}')
    return Matrix44.translate(shift_x, shift_y, 0)


def group_contour_and_holes(
        paths: Iterable[Path]) -> Iterable[Tuple[Path, List[Path]]]:
    """ Group paths created from text strings or entities by their contour
    paths. e.g. "abc" yields 3 [contour, holes] structures::

        ff = fonts.FontFace(family="Arial")
        paths = make_paths_from_str("abc", ff)

        for contour, holes in group_contour_and_holes(paths)
            for hole in holes:
                # hole is a Path() object
                pass

    This is the basic tool to create HATCH entities from paths.

    Warning: This function does not detect separated characters, e.g. "!"
    creates 2 contour paths.

    """
    polygons = nesting.fast_bbox_detection(paths)
    for polygon in polygons:
        contour = polygon[0]
        if len(polygon) > 1:  # are holes present?
            # holes can be recursive polygons, so flatten holes:
            holes = list(nesting.flatten_polygons(polygon[1]))
        else:
            holes = []
        yield contour, holes


def make_hatches_from_str(s: str,
                          font: fonts.FontFace,
                          halign: int = const.LEFT,
                          valign: int = const.BASELINE,
                          segments: int = 4,
                          dxfattribs: Dict = None,
                          m: Matrix44 = None) -> List[Hatch]:
    """ Convert a single line string `s` into a list of virtual
    :class:`~ezdxf.entities.Hatch` entities.
    The path objects are created for the text height of one drawing unit as cap
    height (height of uppercase letter "X") and the insertion point is (0, 0).
    The HATCH entities are aligned to this insertion point. BASELINE means the
    bottom of the letter "X".

    Args:
         s: text to convert
         font: font face definition
         halign: horizontal alignment: LEFT=0, CENTER=1, RIGHT=2
         valign: vertical alignment: BASELINE=0, BOTTOM=1, MIDDLE=2, TOP=3
         segments: minimal segment count per Bézier curve
         dxfattribs: additional DXF attributes
         m: transformation :class:`~ezdxf.math.Matrix44`

    """
    font_properties, font_measurements = _get_font_data(font)
    paths = _str_to_paths(s, font_properties)

    # HATCH is an OCS entity, transforming just the polyline paths
    # is not correct! The Hatch has to be created in the xy-plane!
    hatches = []
    dxfattribs = dxfattribs or dict()
    dxfattribs.setdefault('solid_fill', 1)
    dxfattribs.setdefault('pattern_name', 'SOLID')
    dxfattribs.setdefault('color', 7)

    for contour, holes in group_contour_and_holes(paths):
        hatch = Hatch.new(dxfattribs=dxfattribs)
        hatch.paths.add_polyline_path(
            contour.flattening(1, segments=segments), flags=1)  # 1=external
        for hole in holes:
            hatch.paths.add_polyline_path(
                hole.flattening(1, segments=segments), flags=0)  # 0=normal
        hatches.append(hatch)

    bbox = path.bbox(paths, precise=False)
    matrix = get_alignment_transformation(
        font_measurements, bbox, halign, valign)
    if m is not None:
        matrix *= m

    # Transform HATCH entities as a unit:
    return [hatch.transform(matrix) for hatch in hatches]


def make_paths_from_entity(entity: AnyText) -> List[Path]:
    """ Convert text content from DXF entities TEXT, ATTRIB and ATTDEF into a
    list of :class:`~ezdxf.render.Path` objects. All paths are returned in a
    single list.
    The paths are located at the location of the source entity, but don't expect
    a 100% match compared to CAD applications.

    """
    return []


def make_hatches_from_entity(entity: AnyText) -> List[Hatch]:
    """ Convert text content from DXF entities TEXT, ATTRIB and ATTDEF into a
    list of virtual :class:`~ezdxf.entities.Hatch` entities.
    The hatches are located at the location of the source entity, but don't
    expect a 100% match compared to CAD applications.

    """
    return []
