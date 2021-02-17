#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Union, List, Dict, Tuple
import math
import enum
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties, findfont

from ezdxf.entities import Text, Attrib, Hatch
from ezdxf.lldxf import const
from ezdxf.math import Matrix44, BoundingBox, Vec3
from ezdxf import path
from ezdxf.path import Path
from ezdxf.tools import fonts
from ezdxf.query import EntityQuery

__all__ = [
    "make_paths_from_str", "make_hatches_from_str", "make_paths_from_entity",
    "make_hatches_from_entity", "explode",
]

AnyText = Union[Text, Attrib]
VALID_TYPES = ('TEXT', 'ATTRIB')


def make_paths_from_str(s: str,
                        font: fonts.FontFace,
                        size: float = 1.0,
                        align: str = 'LEFT',
                        length: float = 0,
                        m: Matrix44 = None) -> List[Path]:
    """ Convert a single line string `s` into a list of
    :class:`~ezdxf.path.Path` objects. All paths are returned in a single
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
    if len(s) == 0:
        return []
    font_properties, font_measurements = _get_font_data(font)
    # scale font rendering units to drawing units:
    render_size = size / font_measurements.cap_height
    paths = _str_to_paths(s, font_properties, render_size)
    bbox = path.bbox(paths, flatten=False)
    halign, valign = const.TEXT_ALIGN_FLAGS[align.upper()]

    # Text is rendered in drawing units,
    # therefore do alignment in drawing units:
    draw_units_fm = font_measurements.scale_from_baseline(size)
    matrix = get_alignment_transformation(draw_units_fm, bbox, halign, valign)

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
    cap_height = fm.cap_height
    descender_height = fm.descender_height
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


def make_hatches_from_str(s: str,
                          font: fonts.FontFace,
                          size: float = 1.0,
                          align: str = 'LEFT',
                          length: float = 0,
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
         dxfattribs: additional DXF attributes
         m: transformation :class:`~ezdxf.math.Matrix44`

    """
    # HATCH is an OCS entity, transforming just the polyline paths
    # is not correct! The Hatch has to be created in the xy-plane!
    paths = make_paths_from_str(s, font, size, align, length)
    dxfattribs = dxfattribs or dict()
    dxfattribs.setdefault('solid_fill', 1)
    dxfattribs.setdefault('pattern_name', 'SOLID')
    dxfattribs.setdefault('color', const.BYLAYER)
    hatches = path.to_hatches(
        paths, edge_path=True, dxfattribs=dxfattribs)
    if m is not None:
        # Transform HATCH entities as a unit:
        return [hatch.transform(m) for hatch in hatches]
    else:
        return list(hatches)


def check_entity_type(entity):
    if entity is None:
        raise TypeError('entity is None')
    elif not entity.dxftype() in VALID_TYPES:
        raise TypeError(f'unsupported entity type: {entity.dxftype()}')


def make_paths_from_entity(entity: AnyText) -> List[Path]:
    """ Convert text content from DXF entities TEXT and ATTRIB into a
    list of :class:`~ezdxf.path.Path` objects. All paths are returned in a
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
        if ocs.transform:  # to WCS
            m *= ocs.matrix
        return m

    check_entity_type(entity)
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
    The hatches are placed at the same location as the source entity and have
    the same DXF attributes as the source entity.
    Don't expect a 100% match compared to CAD applications.

    """
    check_entity_type(entity)
    extrusion = entity.dxf.extrusion
    attribs = entity.graphic_properties()
    paths = make_paths_from_entity(entity)
    return list(path.to_hatches(
        paths,
        edge_path=True,
        extrusion=extrusion,
        dxfattribs=attribs,
    ))


@enum.unique
class ExplodeType(enum.IntEnum):
    HATCHES = 1
    SPLINES = 2
    LWPOLYLINES = 4


def explode(entity: AnyText, kind: int = 1, target=None) -> EntityQuery:
    """ Explode the text content of DXF entities TEXT and ATTRIB into
    SPLINE and 3D POLYLINE entities or approximated LWPOLYLINE entities
    as outlines as HATCH entities as fillings.
    The target layout is given by the `target` argument, if `target` is ``None``
    the target layout is the source layout of the text entity.

    The `kind` argument defines the DXF types to create as bit flags, e.g. 1+2
    to get HATCHES as filling and SPLINES and POLYLINES as outline:

    === ==============================
    1   :class:`~ezdxf.entities.Hatch` entities as filling
    2   :class:`~ezdxf.entities.Spline` and 3D :class:`~ezdxf.entities.Polyline`
        entities as outline
    4   :class:`~ezdxf.entities.LWPolyline` entities as outline
    === ==============================

    Returns the created DXF entities as an :class:`~ezdxf.query.EntityQuery`
    object. The source entity will be destroyed.

    Don't expect a 100% match compared to CAD applications.

    Args:
        entity: TEXT or ATTRIB entity to explode
        kind: kind of entities to create, 1=HATCHES, 2=SPLINES, 4=LWPOLYLINES
            as bit flags
        target: target layout for new created DXF entities, ``None`` for the
            same layout as the source entity.

    """
    check_entity_type(entity)
    extrusion = entity.dxf.extrusion
    attribs = entity.graphic_properties()
    entities = []

    if kind & ExplodeType.HATCHES:
        entities.extend(make_hatches_from_entity(entity))
    if kind & (ExplodeType.SPLINES + ExplodeType.LWPOLYLINES):
        paths = make_paths_from_entity(entity)
        if kind & ExplodeType.SPLINES:
            entities.extend(path.to_splines_and_polylines(
                paths, dxfattribs=attribs))
        if kind & ExplodeType.LWPOLYLINES:
            entities.extend(path.to_lwpolylines(
                paths, extrusion=extrusion, dxfattribs=attribs))

    # Explicit check for None is required, because empty layouts are also False
    if target is None:
        target = entity.get_layout()
    entity.destroy()

    if target is not None:
        for e in entities:
            target.add_entity(e)
    return EntityQuery(entities)
