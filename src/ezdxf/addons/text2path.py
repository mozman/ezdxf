#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Union, List, Dict, Iterable, Tuple
import math
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties, findfont

from ezdxf.entities import Text, Attrib, Hatch, DXFGraphic
from ezdxf.lldxf import const
from ezdxf.math import Matrix44, BoundingBox
from ezdxf.render import path, nesting, Path
from ezdxf.tools import fonts
from ezdxf.query import EntityQuery

AnyText = Union[Text, Attrib]


def make_paths_from_str(s: str,
                        font: fonts.FontFace,
                        align: str = 'LEFT',
                        length: float = 0,
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
         align: alignment as string, default is "LEFT"
         length: target length for the "ALIGNED" and "FIT" alignments
         m: transformation :class:`~ezdxf.math.Matrix44`

    """
    font_properties, font_measurements = _get_font_data(font)
    paths = _str_to_paths(s, font_properties)
    bbox = path.bbox(paths, precise=False)
    halign, valign = const.TEXT_ALIGN_FLAGS[align.upper()]
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
            holes = list(nesting.flatten_polygons(polygon[1:]))
        else:
            holes = []
        yield contour, holes


def make_hatches_from_str(s: str,
                          font: fonts.FontFace,
                          align: str = 'LEFT',
                          length: float = 0,
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
         align: alignment as string, default is "LEFT"
         length: target length for the "ALIGNED" and "FIT" alignments
         segments: minimal segment count per Bézier curve
         dxfattribs: additional DXF attributes
         m: transformation :class:`~ezdxf.math.Matrix44`

    """
    font_properties, font_measurements = _get_font_data(font)
    paths = _str_to_paths(s, font_properties)
    halign, valign = const.TEXT_ALIGN_FLAGS[align.upper()]
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
    """ Convert text content from DXF entities TEXT and ATTRIB into a
    list of :class:`~ezdxf.render.Path` objects. All paths are returned in a
    single list.
    The paths are located at the location of the source entity, but don't expect
    a 100% match compared to CAD applications.

    """

    def get_font_name():
        font_name = 'arial.ttf'
        style_name = entity.dxf.style
        if entity.doc:
            try:
                style = entity.doc.styles.get(style_name)
                font_name = style.dxf.font
            except ValueError:
                pass
        return font_name

    def get_transformation():
        if valign == const.BASELINE and halign == const.LEFT:
            location = entity.dxf.insert  # ocs
        else:
            location = entity.dxf.align_point  # ocs
        angle = entity.dxf.rotation
        scale = entity.dxf.height / fm.cap_height
        m = Matrix44.chain(
            Matrix44.scale(scale * entity.dxf.width, scale, 1),
            Matrix44.z_rotate(math.radians(angle)),
            Matrix44.translate(location.x, location.y, location.z),
        )
        ocs = entity.ocs()
        if ocs.transform:
            m *= ocs.matrix
        return m

    if not entity.dxftype() in ('TEXT', 'ATTRIB'):
        raise TypeError(f'unsupported entity type: {entity.dxftype()}')
    fonts.load()
    text = entity.plain_text()
    halign = entity.dxf.halign
    special = 0
    valign = entity.dxf.valign
    font_path = get_font_name()
    ff = fonts.get_font_face(font_path)
    fm = fonts.get_font_measurements(font_path)
    if halign >= const.ALIGNED:
        special = halign  # ALIGNED, MIDDLE, FIT
        halign = const.CENTER
    paths = make_paths_from_str(text, ff, halign, valign)
    m = get_transformation()
    return path.transform_paths(paths, m)


def make_hatches_from_entity(entity: AnyText) -> List[Hatch]:
    """ Convert text content from DXF entities TEXT and ATTRIB into a
    list of virtual :class:`~ezdxf.entities.Hatch` entities.
    The hatches are located at the location of the source entity, but don't
    expect a 100% match compared to CAD applications.

    """
    return []


def explode(entity: AnyText, kind: int = 1, target=None) -> EntityQuery:
    """ Explode the text content of DXF entities TEXT and ATTRIB into
    LWPOLYLINE entities as outlines as HATCH entities as fillings.
    The target layout is given by the `target` argument or the same layout as
    the source entity reside, if `target`is ``None``.

    The `kind` argument defines the DXF types to create:

    === ===============================================
    1   :class:`~ezdxf.entities.Hatch` as filling
    2   :class:`~ezdxf.entities.LWPolyline` as outline
    3   :class:`~ezdxf.entities.Hatch` and :class:`~ezdxf.entities.LWPolyline`
    === ===============================================

    Returns the created DXF entities as an :class:`~ezdxf.query.EntityQuery`
    object.

    The source entity will be destroyed and don't expect a 100% match compared
    to CAD applications.

    Args:
        entity: TEXT or ATTRIB entity to explode
        kind: kind of entities to create, 1=HATCH, 2=LWPOLYLINE, 3=BOTH
        target: target layout for new created DXF entities, ``None`` for the
            same layout as the source entity.

    """
    entities = []
    return EntityQuery(entities)
