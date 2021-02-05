#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Union, List, Dict, Iterable, Tuple
import math
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties, findfont

from ezdxf.entities import Text, Attrib, Hatch
from ezdxf.lldxf import const
from ezdxf.math import Matrix44, BoundingBox, Vec3, Vec2
from ezdxf.render import path, nesting, Path
from ezdxf.tools import fonts
from ezdxf.query import EntityQuery

AnyText = Union[Text, Attrib]


def make_paths_from_str(s: str,
                        font: fonts.FontFace,
                        size: float = 1.0,
                        align: str = 'LEFT',
                        length: float = 0,
                        m: Matrix44 = None) -> List[Path]:
    """ Convert a single line string `s` into a list of
    :class:`~ezdxf.render.path.Path` objects. All paths are returned in a single
    list. The text `size` is the height of the uppercase letter "X" (cap height).
    The paths are aligned about the insertion point at (0, 0).
    BASELINE means the bottom of the letter "X".

    Args:
         s: text to convert
         font: font face definition
         size: text size (cap height) in drawing units
         align: alignment as string, default is "LEFT"
         length: target length for the "ALIGNED" and "FIT" alignments
         m: transformation :class:`~ezdxf.math.Matrix44`

    """
    font_properties, font_measurements = _get_font_data(font)
    scaled_size = size / font_measurements.cap_height
    scaled_fm = font_measurements.scale_from_baseline(scaled_size)
    paths = _str_to_paths(s, font_properties, scaled_size)
    bbox = path.bbox(paths, precise=False)
    halign, valign = const.TEXT_ALIGN_FLAGS[align.upper()]
    matrix = get_alignment_transformation(scaled_fm, bbox, halign, valign)

    stretch_x = 1.0
    stretch_y = 1.0
    if align == 'ALIGNED':
        stretch_x = length / bbox.size.x
        stretch_y = stretch_x
    elif align == 'FIT':
        stretch_x = length / bbox.size.x
    if stretch_x != 1.0:
        matrix *= Matrix44.scale(stretch_x, stretch_y, 1.0)
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


def _str_to_paths(s: str, fp: FontProperties, size: float = 1.0) -> List[Path]:
    text_path = TextPath((0, 0), s, size=size, prop=fp, usetex=False)
    return list(path.from_matplotlib_path(text_path))


def get_alignment_transformation(fm: fonts.FontMeasurements, bbox: BoundingBox,
                                 halign: int, valign: int) -> Matrix44:
    if halign == const.LEFT:
        shift_x = 0
    elif halign == const.RIGHT:
        shift_x = -bbox.extmax.x
    elif halign == const.CENTER or halign > 2:  # ALIGNED, MIDDLE, FIT
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
    if halign == 4:  # MIDDLE
        shift_y = max(fm.total_height, bbox.size.y) / -2.0
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
                          size: float = 1.0,
                          align: str = 'LEFT',
                          length: float = 0,
                          segments: int = 4,
                          dxfattribs: Dict = None,
                          m: Matrix44 = None) -> List[Hatch]:
    """ Convert a single line string `s` into a list of virtual
    :class:`~ezdxf.entities.Hatch` entities.
    The text `size` is the height of the uppercase letter "X" (cap height).
    The paths are aligned about the insertion point at (0, 0).
    The HATCH entities are aligned to this insertion point. BASELINE means the
    bottom of the letter "X".

    Args:
         s: text to convert
         font: font face definition
         size: text size (cap height) in drawing units
         align: alignment as string, default is "LEFT"
         length: target length for the "ALIGNED" and "FIT" alignments
         segments: minimal segment count per Bézier curve
         dxfattribs: additional DXF attributes
         m: transformation :class:`~ezdxf.math.Matrix44`

    """
    font_properties, font_measurements = _get_font_data(font)
    # scale cap_height for 1 drawing unit!
    scaled_size = size / font_measurements.cap_height
    scaled_fm = font_measurements.scale_from_baseline(scaled_size)
    paths = _str_to_paths(s, font_properties, scaled_size)

    # HATCH is an OCS entity, transforming just the polyline paths
    # is not correct! The Hatch has to be created in the xy-plane!
    hatches = []
    dxfattribs = dxfattribs or dict()
    dxfattribs.setdefault('solid_fill', 1)
    dxfattribs.setdefault('pattern_name', 'SOLID')
    dxfattribs.setdefault('color', 7)

    for contour, holes in group_contour_and_holes(paths):
        hatch = Hatch.new(dxfattribs=dxfattribs)
        # Vec2 removes the z-axis, which would be interpreted as bulge value!
        hatch.paths.add_polyline_path(
            Vec2.generate(contour.flattening(1, segments=segments)), flags=1)
        for hole in holes:
            hatch.paths.add_polyline_path(
                Vec2.generate(hole.flattening(1, segments=segments)), flags=0)
        hatches.append(hatch)

    halign, valign = const.TEXT_ALIGN_FLAGS[align.upper()]
    bbox = path.bbox(paths, precise=False)
    matrix = get_alignment_transformation(scaled_fm, bbox, halign, valign)
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
        """ Apply rotation, width factor, translation to the insertion point
        and if necessary transformation from OCS to WCS.
        """
        # TODO: text generation flags - mirror-x and mirror-y
        angle = math.radians(entity.dxf.rotation)
        width_factor = entity.dxf.width
        if align == 'LEFT':
            location = p1
        elif align in ('ALIGNED', 'FIT'):
            width_factor = 1.0  # text goes from p1 to p2, no stretching applied
            location = p1.lerp(p2, factor=0.5)
            angle = (p2 - p1).angle  # override stored angle
        else:
            location = p2
        m = Matrix44.chain(
            Matrix44.scale(width_factor, 1, 1),
            Matrix44.z_rotate(angle),
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
    align = entity.get_align()
    p1 = Vec3(entity.dxf.insert)
    if entity.dxf.hasattr('align_point'):
        p2 = Vec3(entity.dxf.align_point)
    else:
        p2 = p1

    length = 0
    if align in ('FIT', 'ALIGNED'):
        # text is stretch between p1 and p2
        length = p1.distance(p2)
    paths = make_paths_from_str(
        text, fonts.get_font_face(get_font_name()),
        size=entity.dxf.height,  # cap height in drawing units
        align=align,
        length=length,
    )
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
