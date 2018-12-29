# Created: 10.03.2013
# Copyright (c) 2013-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Sequence, Union, Dict, Tuple, cast
import math
from ezdxf.lldxf import const
from ezdxf.lldxf.const import DXFValueError, DXFVersionError
from ezdxf.algebra import Vector
from ezdxf.algebra import bspline_control_frame, bspline_control_frame_approx

if TYPE_CHECKING:  # import forward references
    from eztypes import DXFFactoryType, DXFEntity, Spline, Text, ImageDef, Image, Line, Point, Circle, Arc, Shape
    from eztypes import Solid, Trace, Face, Insert, Attrib, Polyline, Polyface, Polymesh, UnderlayDef, Underlay
    from eztypes import Hatch, Mesh, LWPolyline, Ellipse, MText, Ray, XLine, Dimension
    from eztypes import Solid3d, Region, Body, Surface, RevolvedSurface, ExtrudedSurface, SweptSurface, LoftedSurface
    from ezdxf.algebra.ucs import UCS

Vertex = Union[Sequence[float], Vector]


def copy_attribs(dxfattribs: dict = None) -> dict:
    return dict(dxfattribs or {})


class GraphicsFactory:
    """ Abstract base class for BaseLayout()
    """

    def __init__(self, dxffactory: 'DXFFactoryType'):
        self._dxffactory = dxffactory

    @property
    def dxfversion(self) -> str:
        return self._dxffactory.dxfversion

    def build_and_add_entity(self, type_: str, dxfattribs: dict):
        raise NotImplementedError("Abstract method call.")

    def add_point(self, location: Vertex, dxfattribs: dict = None) -> 'Point':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['location'] = location
        return self.build_and_add_entity('POINT', dxfattribs)

    def add_line(self, start: Vertex, end: Vertex, dxfattribs: dict = None) -> 'Line':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['start'] = start
        dxfattribs['end'] = end
        return self.build_and_add_entity('LINE', dxfattribs)

    def add_circle(self, center: Vertex, radius: float, dxfattribs: dict = None) -> 'Circle':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['center'] = center
        dxfattribs['radius'] = radius
        return self.build_and_add_entity('CIRCLE', dxfattribs)

    def add_arc(self, center: Vertex, radius: float, start_angle: float, end_angle: float,
                is_counter_clockwise: bool = True, dxfattribs: dict = None) -> 'Arc':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['center'] = center
        dxfattribs['radius'] = radius
        if is_counter_clockwise:
            dxfattribs['start_angle'] = start_angle
            dxfattribs['end_angle'] = end_angle
        else:
            dxfattribs['start_angle'] = end_angle
            dxfattribs['end_angle'] = start_angle
        return self.build_and_add_entity('ARC', dxfattribs)

    def add_solid(self, points: Iterable[Vertex], dxfattribs: dict = None) -> 'Solid':
        return cast('Solid', self._add_quadrilateral('SOLID', points, dxfattribs))

    def add_trace(self, points: Iterable[Vertex], dxfattribs: dict = None) -> 'Trace':
        return cast('Trace', self._add_quadrilateral('TRACE', points, dxfattribs))

    def add_3dface(self, points: Iterable[Vertex], dxfattribs: dict = None) -> 'Face':
        return cast('Face', self._add_quadrilateral('3DFACE', points, dxfattribs))

    def add_text(self, text: str, dxfattribs: dict = None) -> 'Text':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['text'] = text
        dxfattribs.setdefault('insert', (0, 0))
        return self.build_and_add_entity('TEXT', dxfattribs)

    def add_blockref(self, name: str, insert: Vertex, dxfattribs: dict = None) -> 'Insert':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['name'] = name
        dxfattribs['insert'] = insert
        blockref = self.build_and_add_entity('INSERT', dxfattribs)
        return blockref

    def add_auto_blockref(self, name: str, insert: Vertex, values: Dict[str, str], dxfattribs: dict = None) \
            -> 'Insert':
        def get_dxfattribs(attdef) -> dict:
            dxfattribs = attdef.dxfattribs()
            dxfattribs.pop('prompt', None)
            dxfattribs.pop('handle', None)
            return dxfattribs

        def unpack(dxfattribs) -> Tuple[str, str, Vertex]:
            tag = dxfattribs.pop('tag')
            text = values.get(tag, "")
            insert = dxfattribs.pop('insert')
            return tag, text, insert

        def autofill(blockref, blockdef) -> None:
            # ATTRIBs are placed relative to the base point
            for attdef in blockdef.attdefs():
                dxfattribs = get_dxfattribs(attdef)
                tag, text, insert = unpack(dxfattribs)
                blockref.add_attrib(tag, text, insert, dxfattribs)

        dxfattribs = copy_attribs(dxfattribs)
        autoblock = self._dxffactory.blocks.new_anonymous_block()
        blockref = autoblock.add_blockref(name, (0, 0))
        blockdef = self._dxffactory.blocks[name]
        autofill(blockref, blockdef)
        return self.add_blockref(autoblock.name, insert, dxfattribs)

    def add_attrib(self, tag: str, text: str, insert: Vertex = (0, 0), dxfattribs: dict = None) -> 'Attrib':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['tag'] = tag
        dxfattribs['text'] = text
        dxfattribs['insert'] = insert
        return self.build_and_add_entity('ATTRIB', dxfattribs)

    def add_polyline2d(self, points: Iterable[Vertex], dxfattribs: dict = None) -> 'Polyline':
        dxfattribs = copy_attribs(dxfattribs)
        closed = dxfattribs.pop('closed', False)
        polyline = self.build_and_add_entity('POLYLINE', dxfattribs)
        polyline.close(closed)
        polyline.append_vertices(points)
        return polyline

    def add_polyline3d(self, points: Iterable[Vertex], dxfattribs: dict = None) -> 'Polyline':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | const.POLYLINE_3D_POLYLINE
        return self.add_polyline2d(points, dxfattribs)

    def add_polymesh(self, size: Tuple[int, int] = (3, 3), dxfattribs: dict = None) -> 'Polymesh':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | const.POLYLINE_3D_POLYMESH
        m_size = max(size[0], 2)
        n_size = max(size[1], 2)
        dxfattribs['m_count'] = m_size
        dxfattribs['n_count'] = n_size
        m_close = dxfattribs.pop('m_close', False)
        n_close = dxfattribs.pop('n_close', False)
        polymesh = self.build_and_add_entity('POLYLINE', dxfattribs)

        points = [(0, 0, 0)] * (m_size * n_size)
        polymesh.append_vertices(points)  # init mesh vertices
        polymesh.close(m_close, n_close)
        return polymesh.cast()

    def add_polyface(self, dxfattribs: dict = None) -> 'Polyface':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | const.POLYLINE_POLYFACE
        m_close = dxfattribs.pop('m_close', False)
        n_close = dxfattribs.pop('n_close', False)
        polyface = self.build_and_add_entity('POLYLINE', dxfattribs)
        polyface.close(m_close, n_close)
        return polyface.cast()

    def _add_quadrilateral(self, type_: str, points: Iterable[Vertex], dxfattribs: dict = None) -> 'DXFEntity':
        dxfattribs = copy_attribs(dxfattribs)
        entity = self.build_and_add_entity(type_, dxfattribs)
        for x, point in enumerate(self._four_points(points)):
            entity[x] = point
        return entity

    @staticmethod
    def _four_points(points: Iterable[Vertex]) -> Iterable[Vertex]:
        vertices = list(points)
        if len(vertices) not in (3, 4):
            raise DXFValueError('3 or 4 points required.')
        for vertex in vertices:
            yield vertex
        if len(vertices) == 3:
            yield vertices[-1]  # last again

    def add_shape(self, name: str, insert: Vertex = (0, 0), size: float = 1.0, dxfattribs: dict = None) -> 'Shape':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['name'] = name
        dxfattribs['insert'] = insert
        dxfattribs['size'] = size
        return self.build_and_add_entity('SHAPE', dxfattribs)

    # new entities in DXF AC1015 (R2000)

    def add_lwpolyline(self, points: Iterable[Vertex], dxfattribs: dict = None) -> 'LWPolyline':
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('LWPOLYLINE requires DXF version R2000+')
        dxfattribs = copy_attribs(dxfattribs)
        closed = dxfattribs.pop('closed', False)
        lwpolyline = self.build_and_add_entity('LWPOLYLINE', dxfattribs)
        lwpolyline.set_points(points)
        lwpolyline.closed = closed
        return lwpolyline

    def add_ellipse(self, center: Vertex, major_axis: Vertex = (1, 0, 0), ratio: float = 1, start_param: float = 0,
                    end_param: float = 6.283185307, dxfattribs: dict = None) -> 'Ellipse':
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('ELLIPSE requires DXF version R2000+')
        if ratio > 1.:
            raise DXFValueError("Parameter 'ratio' has to be <= 1.0")

        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['center'] = center
        dxfattribs['major_axis'] = major_axis
        dxfattribs['ratio'] = ratio
        dxfattribs['start_param'] = start_param
        dxfattribs['end_param'] = end_param
        return self.build_and_add_entity('ELLIPSE', dxfattribs)

    def add_mtext(self, text: str, dxfattribs: dict = None) -> 'MText':
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('MTEXT requires DXF version R2000+')
        dxfattribs = copy_attribs(dxfattribs)
        mtext = self.build_and_add_entity('MTEXT', dxfattribs)
        mtext.set_text(text)
        return mtext

    def add_ray(self, start: Vertex, unit_vector: Vertex, dxfattribs: dict = None) -> 'Ray':
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('RAY requires DXF version R2000+')
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['start'] = start
        dxfattribs['unit_vector'] = unit_vector
        return self.build_and_add_entity('RAY', dxfattribs)

    def add_xline(self, start: Vertex, unit_vector: Vertex, dxfattribs: dict = None) -> 'XLine':
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('XLINE requires DXF version R2000+')
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['start'] = start
        dxfattribs['unit_vector'] = unit_vector
        return self.build_and_add_entity('XLINE', dxfattribs)

    def add_spline(self, fit_points: Iterable[Vertex] = None, degree: int = 3, dxfattribs: dict = None) -> 'Spline':
        """
        Add a B-spline defined by fit points, the control points and knot values are created by the CAD application,
        therefore it is not predictable how the rendered spline will look like, because for every set of fit points
        exists an infinite set of B-splines. If fit_points is None, an 'empty' spline will be created, all data has to
        be set by the user.

        Args:
            fit_points: list of fit points as (x, y[, z]) tuples, if None -> user defined spline
            degree: degree fo B-spline
            dxfattribs: DXF attributes for the SPLINE entity

        Returns: DXF Spline() object

        """
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('SPLINE requires DXF version R2000+')
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['degree'] = degree
        spline = self.build_and_add_entity('SPLINE', dxfattribs)
        if fit_points is not None:
            spline.set_fit_points(list(fit_points))
        return spline

    def add_spline_control_frame(self, fit_points: Iterable[Vertex], degree: int = 3, method: str = 'distance',
                                 power: float = .5, dxfattribs: dict = None) -> 'Spline':
        """
        Create and add B-spline control frame from fit points.

            1. method = 'uniform', creates a uniform t vector, [0 .. 1] equally spaced
            2. method = 'distance', creates a t vector with values proportional to the fit point distances
            3. method = 'centripetal', creates a t vector with values proportional to the fit point distances^power

        None of this methods matches the spline created from fit points by AutoCAD.

        Args:
            fit_points: fit points of B-spline
            degree: degree of B-spline
            method: calculation method for parameter vector t
            power: power for centripetal method
            dxfattribs: DXF attributes for SPLINE entity

        Returns: DXF Spline() object

        """
        bspline = bspline_control_frame(fit_points, degree=degree, method=method, power=power)
        return self.add_open_spline(
            control_points=bspline.control_points,
            degree=bspline.degree,
            knots=bspline.knot_values(),
            dxfattribs=dxfattribs,
        )

    def add_spline_approx(self, fit_points: Iterable[Vertex], count: int, degree: int = 3, method: str = 'distance',
                          power: float = .5, dxfattribs: dict = None) -> 'Spline':
        """
        Approximate B-spline by a reduced count of control points, given are the fit points and the degree of the B-spline.

            1. method = 'uniform', creates a uniform t vector, [0 .. 1] equally spaced
            2. method = 'distance', creates a t vector with values proportional to the fit point distances
            3. method = 'centripetal', creates a t vector with values proportional to the fit point distances^power

        Args:
            fit_points: all fit points of B-spline
            count: count of designated control points
            degree: degree of B-spline
            method: calculation method for parameter vector t
            power: power for centripetal method
            dxfattribs: DXF attributes for SPLINE entity

        Returns: DXF Spline() object

        """
        bspline = bspline_control_frame_approx(fit_points, count, degree=degree, method=method, power=power)
        return self.add_open_spline(
            control_points=bspline.control_points,
            degree=bspline.degree,
            dxfattribs=dxfattribs,
        )

    def add_open_spline(self, control_points: Iterable[Vertex], degree: int = 3, knots: Iterable[float] = None,
                        dxfattribs: dict = None) -> 'Spline':
        spline = self.add_spline(dxfattribs=dxfattribs)
        spline.set_open_uniform(list(control_points), degree)
        if knots is not None:
            spline.set_knot_values(list(knots))
        return spline

    def add_closed_spline(self, control_points: Iterable[Vertex], degree: int = 3, knots: Iterable[float] = None,
                          dxfattribs: dict = None) -> 'Spline':
        spline = self.add_spline(dxfattribs=dxfattribs)
        spline.set_periodic(list(control_points), degree)
        if knots is not None:
            spline.set_knot_values(list(knots))
        return spline

    def add_rational_spline(self, control_points: Iterable[Vertex], weights: Sequence[float], degree: int = 3,
                            knots: Iterable[float] = None, dxfattribs: dict = None) -> 'Spline':
        spline = self.add_spline(dxfattribs=dxfattribs)
        spline.set_open_rational(list(control_points), weights, degree)
        if knots is not None:
            spline.set_knot_values(list(knots))
        return spline

    def add_closed_rational_spline(self, control_points: Iterable[Vertex], weights: Sequence[float], degree: int = 3,
                                   knots: Iterable[float] = None, dxfattribs: dict = None) -> 'Spline':
        spline = self.add_spline(dxfattribs=dxfattribs)
        spline.set_periodic_rational(list(control_points), weights, degree)
        if knots is not None:
            spline.set_knot_values(list(knots))
        return spline

    def add_body(self, acis_data: str = None, dxfattribs: dict = None) -> 'Body':
        return self._add_acis_entiy('BODY', acis_data, dxfattribs)

    def add_region(self, acis_data: str = None, dxfattribs: dict = None) -> 'Region':
        return cast('Region', self._add_acis_entiy('REGION', acis_data, dxfattribs))

    def add_3dsolid(self, acis_data: str = None, dxfattribs: dict = None) -> 'Solid3d':
        return cast('Solid3d', self._add_acis_entiy('3DSOLID', acis_data, dxfattribs))

    def add_surface(self, acis_data: str = None, dxfattribs: dict = None) -> 'Surface':
        if self.dxfversion < 'AC1021':
            raise DXFVersionError('SURFACE requires DXF version R2007+')
        return cast('Surface', self._add_acis_entiy('SURFACE', acis_data, dxfattribs))

    def add_extruded_surface(self, acis_data: str = None, dxfattribs: dict = None) -> 'ExtrudedSurface':
        if self.dxfversion < 'AC1021':
            raise DXFVersionError('EXTRUDEDSURFACE requires DXF version R2007+')
        return cast('ExtrudedSurface', self._add_acis_entiy('EXTRUDEDSURFACE', acis_data, dxfattribs))

    def add_lofted_surface(self, acis_data: str = None, dxfattribs: dict = None) -> 'LoftedSurface':
        if self.dxfversion < 'AC1021':
            raise DXFVersionError('LOFTEDSURFACE requires DXF version R2007+')
        return cast('LoftedSurface', self._add_acis_entiy('LOFTEDSURFACE', acis_data, dxfattribs))

    def add_revolved_surface(self, acis_data: str = None, dxfattribs: dict = None) -> 'RevolvedSurface':
        if self.dxfversion < 'AC1021':
            raise DXFVersionError('REVOLVEDSURFACE requires DXF version R2007+')
        return cast('RevolvedSurface', self._add_acis_entiy('REVOLVEDSURFACE', acis_data, dxfattribs))

    def add_swept_surface(self, acis_data: str = None, dxfattribs: dict = None) -> 'SweptSurface':
        if self.dxfversion < 'AC1021':
            raise DXFVersionError('SWEPT requires DXF version R2007+')
        return cast('SweptSurface', self._add_acis_entiy('SWEPTSURFACE', acis_data, dxfattribs))

    def _add_acis_entiy(self, name, acis_data: str, dxfattribs: dict) -> 'Body':
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('{} requires DXF version R2000+'.format(name))
        dxfattribs = copy_attribs(dxfattribs)
        entity = self.build_and_add_entity(name, dxfattribs)
        if acis_data is not None:
            entity.set_acis_data(acis_data)
        return entity

    def add_hatch(self, color: int = 7, dxfattribs: dict = None) -> 'Hatch':
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('HATCH requires DXF version R2000+')
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['solid_fill'] = 1
        dxfattribs['color'] = color
        dxfattribs['pattern_name'] = 'SOLID'
        return self.build_and_add_entity('HATCH', dxfattribs)

    def add_mesh(self, dxfattribs: dict = None) -> 'Mesh':
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('MESH requires DXF version R2000+')
        dxfattribs = copy_attribs(dxfattribs)
        return self.build_and_add_entity('MESH', dxfattribs)

    def add_image(self, image_def: 'ImageDef', insert: Vertex, size_in_units: Tuple[float, float], rotation: float = 0.,
                  dxfattribs: dict = None) -> 'Image':
        def to_vector(units_per_pixel, angle_in_rad):
            x = math.cos(angle_in_rad) * units_per_pixel
            y = math.sin(angle_in_rad) * units_per_pixel
            return round(x, 6), round(y, 6), 0  # supports only images in the xy-plane

        if self.dxfversion < 'AC1015':
            raise DXFVersionError('IMAGE requires DXF version R2000+')
        dxfattribs = copy_attribs(dxfattribs)
        x_pixels, y_pixels = image_def.dxf.image_size
        x_units, y_units = size_in_units
        x_units_per_pixel = x_units / x_pixels
        y_units_per_pixel = y_units / y_pixels
        x_angle_rad = math.radians(rotation)
        y_angle_rad = x_angle_rad + (math.pi / 2.)

        dxfattribs['insert'] = Vector(insert)
        dxfattribs['u_pixel'] = to_vector(x_units_per_pixel, x_angle_rad)
        dxfattribs['v_pixel'] = to_vector(y_units_per_pixel, y_angle_rad)
        dxfattribs['image_def'] = image_def.dxf.handle
        dxfattribs['image_size'] = image_def.dxf.image_size

        image = self.build_and_add_entity('IMAGE', dxfattribs)
        if self.drawing is not None:
            image_def_reactor = self.drawing.objects.add_image_def_reactor(image.dxf.handle)
            reactor_handle = image_def_reactor.dxf.handle
            image.dxf.image_def_reactor = reactor_handle
            image_def.append_reactor_handle(reactor_handle)
        return image

    def add_underlay(self, underlay_def: 'UnderlayDef', insert: Vertex = (0, 0, 0),
                     scale: Tuple[float, float, float] = (1, 1, 1),
                     rotation: float = 0., dxfattribs: dict = None) -> 'Underlay':
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('UNDERLAY requires DXF version R2000+')
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['insert'] = insert
        dxfattribs['underlay_def'] = underlay_def.dxf.handle
        dxfattribs['rotation'] = rotation

        underlay = self.build_and_add_entity(underlay_def.entity_name, dxfattribs)
        underlay.scale = scale
        underlay_def.append_reactor_handle(underlay.dxf.handle)
        return underlay

    def render_dimension(self, dimension: 'Dimension', ucs: 'UCS' = None,  txtstyle: str = None) -> None:
        dwg = cast('Drawing', self.drawing)
        dwg.dimension_renderer.dispatch(dimension, ucs, txtstyle)

    def add_linear_dim(self,
                       base: 'Vertex',
                       ext1: 'Vertex',
                       ext2: 'Vertex',
                       text_midpoint: 'Vertex' = None,
                       dimstyle: str = 'STANDARD',
                       text: str = "<>",
                       angle: float = 0,  # 0=horizontal, 90=vertical, else=rotated
                       text_rotation: float = 0,
                       dxfattribs: dict = None) -> 'Dimension':
        """
        Horizontal, vertical and rotated dimension line. If an UCS is used for dimension line rendering, all point
        definitions in UCS coordinates, translation into WCS and OCS is done by the rendering function. Manual set
        extrusion vector will be replaced by OCS defined by UCS or (0, 0, 1) if no UCS is used.

        To create the necessary geometry, you have to call layout.render_dimension(dimension, ucs) manually, this two
        step process allows additional processing steps on the DIMENSION entity between creation and rendering.

        Args:
            base: definition point, intersection of extension line 1 and dimension line (in UCS)
            ext1: start point of extension line 1 (in UCS)
            ext2: start point of extension line 2 (in UCS)
            text_midpoint: text mid point (in UCS), or None for computed text placing
            text: None or "<>" measurement is drawn as text, " " text is suppressed, else `text` is drawn as text
            dimstyle: dimension style name (DimStyle table entry), default is `STANDARD`
            angle: angle from ucs x-axis to dimension line in degrees
            text_rotation: rotation angle of the dimension text away from its default orientation
                           (the direction of the dimension line) in degrees
            dxfattribs: DXF attributes for DIMENSION entity

        """
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['dimstyle'] = dimstyle
        dxfattribs['defpoint'] = Vector(base)
        dxfattribs['defpoint2'] = Vector(ext1)
        dxfattribs['defpoint3'] = Vector(ext2)
        if text_midpoint:
            dxfattribs['text_midpoint'] = Vector(text_midpoint)
        dxfattribs['text'] = text
        dxfattribs['angle'] = float(angle)
        dxfattribs['text_rotation'] = float(text_rotation)
        dxfattribs['dimtype'] = dimtype(const.DIM_LINEAR, self.dxfversion)
        return cast('Dimension', self.build_and_add_entity('DIMENSION', dxfattribs).cast())

    # def add_aligned_dim(self, dxfattribs: dict = None) -> 'Dimension': dxfattribs = copy_attribs(dxfattribs))
    # don't understand the difference between aligned and linear yet!

    def add_angular_dim(self,
                        dxfattribs: dict = None) -> 'Dimension':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['dimtype'] = dimtype(const.DIM_ANGULAR, self.dxfversion)
        return cast('Dimension', self.build_and_add_entity('DIMENSION', dxfattribs).cast())

    def add_diameter_dim(self,
                         dxfattribs: dict = None) -> 'Dimension':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['dimtype'] = dimtype(const.DIM_DIAMETER, self.dxfversion)
        return cast('Dimension', self.build_and_add_entity('DIMENSION', dxfattribs).cast())

    def add_radius_dim(self,
                       dxfattribs: dict = None) -> 'Dimension':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['dimtype'] = dimtype(const.DIM_RADIUS, self.dxfversion)
        return cast('Dimension', self.build_and_add_entity('DIMENSION', dxfattribs).cast())

    def add_angular_3p_dim(self,
                           dxfattribs: dict = None) -> 'Dimension':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['dimtype'] = dimtype(const.DIM_ANGULAR_3P, self.dxfversion)
        return cast('Dimension', self.build_and_add_entity('DIMENSION', dxfattribs).cast())

    def add_ordinate_dim(self,
                         dxfattribs: dict = None) -> 'Dimension':
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['dimtype'] = dimtype(const.DIM_ORDINATE, self.dxfversion)
        return cast('Dimension', self.build_and_add_entity('DIMENSION', dxfattribs).cast())


def dimtype(dtype: int, dxfversion: str) -> int:
    # always set user defined text location, because replicating the exact AutoCAD placing is not documented
    if dxfversion <= 'AC1009':
        flags = const.DIM_USER_LOCATION_OVERRIDE
    else:
        # every DIMENSION entity has an exclusive geometry BLOCK, this flag is not supported by DXF12 and prior
        flags = const.DIM_BLOCK_EXCLUSIVE | const.DIM_USER_LOCATION_OVERRIDE
    return dtype | flags
