# Created: 10.03.2013
# Copyright (c) 2013-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Sequence, Dict, Tuple, cast
import math
import logging

from ezdxf.lldxf import const
from ezdxf.lldxf.const import DXFValueError, DXFVersionError, DXF2000, DXF2007
from ezdxf.math import Vector, global_bspline_interpolation
from ezdxf.render.arrows import ARROWS
from ezdxf.entities.dimstyleoverride import DimStyleOverride
from ezdxf.render.dim_linear import multi_point_linear_dimension

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        UCS, Vertex, Drawing, DXFGraphic, Line, Arc, Circle, Point, Polyline,
        Shape, Solid, Trace, Face3d, Insert, Attrib, Polyface, Polymesh, Text,
        LWPolyline, Ellipse, MText, XLine, Ray, Spline, Leader, AttDef, Mesh,
        Hatch, Image, ImageDef, Underlay, UnderlayDef, Body, Region, Solid3d,
        LoftedSurface, Surface, RevolvedSurface, ExtrudedSurface, SweptSurface,
        Wipeout,
    )


class CreatorInterface:
    def __init__(self, doc: 'Drawing'):
        self.doc = doc

    # todo: for compatibility
    @property
    def drawing(self):
        return self.doc

    @property
    def dxfversion(self) -> str:
        return self.doc.dxfversion

    @property
    def dxffactory(self):
        return self.doc.dxffactory

    @property
    def is_active_paperspace(self):
        return False

    def new_entity(self, type_: str, dxfattribs: dict) -> 'DXFGraphic':
        """
        Create entity in drawing database and add entity to the entity space.

        Args:
            type_ : DXF type string, like ``'LINE'``, ``'CIRCLE'`` or
                ``'LWPOLYLINE'``
            dxfattribs: DXF attributes for the new entity

        """
        entity = self.dxffactory.create_db_entry(type_, dxfattribs)
        self.add_entity(entity)
        return entity

    def add_entity(self, entity: 'DXFGraphic') -> None:
        pass

    def add_point(self, location: 'Vertex', dxfattribs: dict = None) -> 'Point':
        """
        Add a :class:`~ezdxf.entities.Point` entity at `location`.

        Args:
            location: 2D/3D point in :ref:`WCS`
            dxfattribs: additional DXF attributes

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['location'] = Vector(location)
        return self.new_entity('POINT', dxfattribs)

    def add_line(self, start: 'Vertex', end: 'Vertex',
                 dxfattribs: dict = None) -> 'Line':
        """
        Add a :class:`~ezdxf.entities.Line` entity from `start` to `end`.

        Args:
            start: 2D/3D point in :ref:`WCS`
            end: 2D/3D point in :ref:`WCS`
            dxfattribs: additional DXF attributes

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['start'] = Vector(start)
        dxfattribs['end'] = Vector(end)
        return self.new_entity('LINE', dxfattribs)

    def add_circle(self, center: 'Vertex', radius: float,
                   dxfattribs: dict = None) -> 'Circle':
        """
        Add a :class:`~ezdxf.entities.Circle` entity. This is an 2D element,
        which can be placed in space by using :ref:`OCS`.

        Args:
            center: 2D/3D point in :ref:`WCS`
            radius: circle radius
            dxfattribs: additional DXF attributes

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['center'] = Vector(center)
        dxfattribs['radius'] = float(radius)
        return self.new_entity('CIRCLE', dxfattribs)

    def add_ellipse(self, center: 'Vertex', major_axis: 'Vertex' = (1, 0, 0),
                    ratio: float = 1, start_param: float = 0,
                    end_param: float = math.tau,
                    dxfattribs: dict = None) -> 'Ellipse':
        """
        Add an :class:`~ezdxf.entities.Ellipse` entity, `ratio` is the ratio of
        minor axis to major axis, `start_param` and `end_param` defines start
        and end point of the ellipse, a full ellipse goes from 0 to 2*pi.
        The ellipse goes from start to end param in `counter clockwise`
        direction.

        Args:
            center: center of ellipse as 2D/3D point in :ref:`WCS`
            major_axis: major axis as vector (x, y, z)
            ratio: ratio of minor axis to major axis in range +/-[1e-6, 1.0]
            start_param: start of ellipse curve
            end_param: end param of ellipse curve
            dxfattribs: additional DXF attributes

        """
        if self.dxfversion < DXF2000:
            raise DXFVersionError('ELLIPSE requires DXF R2000')
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['center'] = Vector(center)
        dxfattribs['major_axis'] = Vector(major_axis)
        dxfattribs['ratio'] = float(ratio)
        dxfattribs['start_param'] = float(start_param)
        dxfattribs['end_param'] = float(end_param)
        return self.new_entity('ELLIPSE', dxfattribs)

    def add_arc(self, center: 'Vertex', radius: float, start_angle: float,
                end_angle: float,
                is_counter_clockwise: bool = True,
                dxfattribs: dict = None) -> 'Arc':
        """
        Add an :class:`~ezdxf.entities.Arc` entity. The arc goes from
        `start_angle` to `end_angle` in counter clockwise direction by default,
        set parameter `is_counter_clockwise` to False for clockwise orientation.

        Args:
            center: center of arc as 2D/3D point in :ref:`WCS`
            radius: arc radius
            start_angle: start angle in degrees
            end_angle: end angle in degrees
            is_counter_clockwise: False for clockwise orientation
            dxfattribs: additional DXF attributes

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['center'] = Vector(center)
        dxfattribs['radius'] = float(radius)
        if is_counter_clockwise:
            dxfattribs['start_angle'] = float(start_angle)
            dxfattribs['end_angle'] = float(end_angle)
        else:
            dxfattribs['start_angle'] = float(end_angle)
            dxfattribs['end_angle'] = float(start_angle)
        return self.new_entity('ARC', dxfattribs)

    def add_solid(self, points: Iterable['Vertex'],
                  dxfattribs: dict = None) -> 'Solid':
        """
        Add a :class:`~ezdxf.entities.Solid` entity, `points` is an iterable
        of 3 or 4 points.

        Args:
            points: iterable of 3 or 4 2D/3D points in :ref:`WCS`
            dxfattribs: additional DXF attributes for :class:`Solid` entity

        """
        return cast('Solid',
                    self._add_quadrilateral('SOLID', points, dxfattribs))

    def add_trace(self, points: Iterable['Vertex'],
                  dxfattribs: dict = None) -> 'Trace':
        """
        Add a :class:`~ezdxf.entities.Trace` entity, `points` is an iterable
        of 3 or 4 points.

        Args:
            points: iterable of 3 or 4 2D/3D points in :ref:`WCS`
            dxfattribs: additional DXF attributes for :class:`Trace`
                entity

        """
        return cast('Trace',
                    self._add_quadrilateral('TRACE', points, dxfattribs))

    def add_3dface(self, points: Iterable['Vertex'],
                   dxfattribs: dict = None) -> 'Face3d':
        """
        Add a :class:`~ezdxf.entities.3DFace` entity, `points` is an iterable
        3 or 4 2D/3D points.

        Args:
            points: iterable of 3 or 4 2D/3D points in :ref:`WCS`
            dxfattribs: additional DXF attributes for :class:`3DFace` entity

        """
        return cast('Face',
                    self._add_quadrilateral('3DFACE', points, dxfattribs))

    def add_text(self, text: str, dxfattribs: dict = None) -> 'Text':
        """
        Add a :class:`~ezdxf.entities.Text` entity, see also :class:`Style`.

        Args:
            text: content string
            dxfattribs: additional DXF attributes for :class:`Text` entity

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['text'] = str(text)
        dxfattribs.setdefault('insert', Vector())
        return self.new_entity('TEXT', dxfattribs)

    def add_blockref(self, name: str, insert: 'Vertex',
                     dxfattribs: dict = None) -> 'Insert':
        """
        Add an :class:`~ezdxf.entities.Insert` entity.

        Args:
            name: block name as str
            insert: insert location as 2D/3D point in :ref:`WCS`
            dxfattribs: additional DXF attributes for :class:`Insert` entity

        """
        if not isinstance(name, str):
            raise DXFValueError('Block name as string required.')

        dxfattribs = dict(dxfattribs or {})
        dxfattribs['name'] = name
        dxfattribs['insert'] = Vector(insert)
        blockref = self.new_entity('INSERT', dxfattribs)  # type: Insert
        return blockref

    def add_auto_blockref(
            self, name: str, insert: 'Vertex', values: Dict[str, str],
            dxfattribs: dict = None) -> 'Insert':
        """
        Add an :class:`~ezdxf.entities.Insert` entity. This method adds for each
        :class:`~ezdxf.entities.Attdef` entity, defined in the block definition,
        automatically an :class:`Attrib` entity to the block reference and set
        ``tag/value`` DXF attributes of the ATTRIB entities by the ``key/value``
        pairs (both as strings) of the `values` dict.

        The Attrib entities are placed relative to the insert point, which is
        equal to the block base point.

        This method wraps the INSERT and all the ATTRIB entities into an
        anonymous block, which produces the best visual results, especially for
        non uniform scaled block references, because the transformation and
        scaling is done by the CAD application. But this makes evaluation of
        block references with attributes more complicated, if you prefer INSERT
        and ATTRIB entities without a wrapper block use the
        :meth:`add_blockref_with_attribs` method.

        Args:
            name: block name
            insert: insert location as 2D/3D point in :ref:`WCS`
            values: :class:`~ezdxf.entities.Attrib` tag values as ``tag/value`` pairs
            dxfattribs: additional DXF attributes for :class:`Insert` entity

        """
        if not isinstance(name, str):
            raise DXFValueError('Block name as string required.')

        def unpack(dxfattribs) -> Tuple[str, str, 'Vertex']:
            tag = dxfattribs.pop('tag')
            text = values.get(tag, "")
            location = dxfattribs.pop('insert')
            return tag, text, location

        def autofill() -> None:
            # ATTRIBs are placed relative to the base point
            for attdef in blockdef.attdefs():
                dxfattribs = attdef.dxfattribs(drop={'prompt', 'handle'})
                tag, text, location = unpack(dxfattribs)
                blockref.add_attrib(tag, text, location, dxfattribs)

        dxfattribs = dict(dxfattribs or {})
        autoblock = self.doc.blocks.new_anonymous_block()
        blockref = autoblock.add_blockref(name, (0, 0))
        blockdef = self.doc.blocks[name]
        autofill()
        return self.add_blockref(autoblock.name, insert, dxfattribs)

    def add_attrib(self, tag: str, text: str, insert: 'Vertex' = (0, 0),
                   dxfattribs: dict = None) -> 'Attrib':
        """
        Add an :class:`~ezdxf.entities.Attrib` as stand alone DXF entity.

        Args:
            tag: tag name as string
            text: tag value as string
            insert: insert location as 2D/3D point in :ref:`WCS`
            dxfattribs: additional DXF attributes for :class:`Attrib` entity

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['tag'] = str(tag)
        dxfattribs['text'] = str(text)
        dxfattribs['insert'] = Vector(insert)
        return self.new_entity('ATTRIB', dxfattribs)

    def add_attdef(self, tag: str, insert: 'Vertex' = (0, 0), text: str = '',
                   dxfattribs: dict = None) -> 'AttDef':
        """
        Add an :class:`~ezdxf.entities.AttDef` as stand alone DXF entity.

        Set position and alignment by the idiom::

            layout.add_attdef('NAME').set_pos((2, 3), align='MIDDLE_CENTER')

        Args:
            tag: tag name as string
            insert: insert location as 2D/3D point in :ref:`WCS`
            text: tag value as string
            dxfattribs: additional DXF attributes

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['tag'] = str(tag)
        dxfattribs['insert'] = Vector(insert)
        dxfattribs['text'] = str(text)
        return self.new_entity('ATTDEF', dxfattribs)

    def add_polyline2d(self, points: Iterable['Vertex'],
                       dxfattribs: dict = None,
                       format: str = None, ) -> 'Polyline':
        """
        Add a 2D :class:`~ezdxf.entities.Polyline` entity.

        Args:
            points: iterable of 2D points in :ref:`WCS`
            dxfattribs: additional DXF attributes
            format: user defined point format like :meth:`add_lwpolyline`,
                default is ``None``

        .. versionadded:: 0.11

            user defined point format

        """
        dxfattribs = dict(dxfattribs or {})
        closed = dxfattribs.pop('closed', False)
        polyline = self.new_entity('POLYLINE', dxfattribs)  # type: Polyline
        polyline.close(closed)
        if format is not None:
            polyline.append_formatted_vertices(points, format=format)
        else:
            polyline.append_vertices(points)
        return polyline

    def add_polyline3d(self, points: Iterable['Vertex'],
                       dxfattribs: dict = None) -> 'Polyline':
        """
        Add a 3D :class:`~ezdxf.entities.Polyline` entity.

        Args:
            points: iterable of 3D points in :ref:`WCS`
            dxfattribs: additional DXF attributes

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['flags'] = dxfattribs.get('flags',
                                             0) | const.POLYLINE_3D_POLYLINE
        return self.add_polyline2d(points, dxfattribs)

    def add_polymesh(self, size: Tuple[int, int] = (3, 3),
                     dxfattribs: dict = None) -> 'Polymesh':
        """
        Add a :class:`~ezdxf.entities.Polymesh` entity, which is a wrapper class
        for the POLYLINE entity. A polymesh is a grid of `mcount` x `ncount`
        vertices and every vertex has its own (x, y, z)-coordinates.

        Args:
            size: 2-tuple (`mcount`, `ncount`)
            dxfattribs: additional DXF attributes for
                :class:`~ezdxf.entities.Polyline` entity

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['flags'] = dxfattribs.get('flags',
                                             0) | const.POLYLINE_3D_POLYMESH
        m_size = max(size[0], 2)
        n_size = max(size[1], 2)
        dxfattribs['m_count'] = m_size
        dxfattribs['n_count'] = n_size
        m_close = dxfattribs.pop('m_close', False)
        n_close = dxfattribs.pop('n_close', False)
        # returns casted entity
        polymesh = self.new_entity('POLYLINE', dxfattribs)  # type: Polymesh

        points = [(0, 0, 0)] * (m_size * n_size)
        polymesh.append_vertices(points)  # init mesh vertices
        polymesh.close(m_close, n_close)
        return polymesh

    def add_polyface(self, dxfattribs: dict = None) -> 'Polyface':
        """ Add a :class:`~ezdxf.entities.Polyface` entity, which is a wrapper
        class for the POLYLINE entity.

        Args:
            dxfattribs: additional DXF attributes for
                :class:`~ezdxf.entities.Polyline` entity

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['flags'] = dxfattribs.get('flags',
                                             0) | const.POLYLINE_POLYFACE
        m_close = dxfattribs.pop('m_close', False)
        n_close = dxfattribs.pop('n_close', False)
        polyface = self.new_entity('POLYLINE', dxfattribs)  # type: Polyface
        polyface.close(m_close, n_close)
        return polyface

    def _add_quadrilateral(self, type_: str, points: Iterable['Vertex'],
                           dxfattribs: dict = None) -> 'DXFGraphic':
        dxfattribs = dict(dxfattribs or {})
        entity = self.new_entity(type_, dxfattribs)
        for x, point in enumerate(self._four_points(points)):
            entity[x] = Vector(point)
        return entity

    @staticmethod
    def _four_points(points: Iterable['Vertex']) -> Iterable['Vertex']:
        vertices = list(points)
        if len(vertices) not in (3, 4):
            raise DXFValueError('3 or 4 points required.')
        for vertex in vertices:
            yield vertex
        if len(vertices) == 3:
            yield vertices[-1]  # last again

    def add_shape(self, name: str, insert: 'Vertex' = (0, 0), size: float = 1.0,
                  dxfattribs: dict = None) -> 'Shape':
        """
        Add a :class:`~ezdxf.entities.Shape` reference to a external stored shape.

        Args:
            name: shape name as string
            insert: insert location as 2D/3D point in :ref:`WCS`
            size: size factor
            dxfattribs: additional DXF attributes

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['name'] = str(name)
        dxfattribs['insert'] = Vector(insert)
        dxfattribs['size'] = float(size)
        return self.new_entity('SHAPE', dxfattribs)

    # new entities in DXF AC1015 (R2000)

    def add_lwpolyline(self, points: Iterable['Vertex'], format: str = 'xyseb',
                       dxfattribs: dict = None) -> 'LWPolyline':
        """
        Add a 2D polyline as :class:`~ezdxf.entities.LWPolyline` entity.
        A points are defined as (x, y, [start_width, [end_width, [bulge]]])
        tuples, but order can be redefined by the `format` argument. Set
        `start_width`, `end_width` to ``0`` to be ignored like
        (x, y, 0, 0, bulge).

        The :class:`~ezdxf.entities.LWPolyline` is defined as a single DXF
        entity and needs less disk space than a
        :class:`~ezdxf.entities.Polyline` entity. (requires DXF R2000)

        Format codes:

            - ``x`` = x-coordinate
            - ``y`` = y-coordinate
            - ``s`` = start width
            - ``e`` = end width
            - ``b`` = bulge value
            - ``v`` = (x, y [,z]) tuple (z-axis is ignored)

        Args:
            points: iterable of (x, y, [start_width, [end_width, [bulge]]]) tuples
            format: user defined point format, default is ``"xyseb"``
            dxfattribs: additional DXF attributes

        """
        if self.dxfversion < DXF2000:
            raise DXFVersionError('LWPOLYLINE requires DXF R2000')
        dxfattribs = dict(dxfattribs or {})
        closed = dxfattribs.pop('closed', False)
        lwpolyline: 'LWPolyline' = self.new_entity('LWPOLYLINE', dxfattribs)
        lwpolyline.set_points(points, format=format)
        lwpolyline.closed = closed
        return lwpolyline

    def add_mtext(self, text: str, dxfattribs: dict = None) -> 'MText':
        """
        Add a multiline text entity with automatic text wrapping at boundaries
        as :class:`~ezdxf.entities.MText` entity.
        (requires DXF R2000)

        Args:
            text: content string
            dxfattribs: additional DXF attributes

        """
        if self.dxfversion < DXF2000:
            raise DXFVersionError('MTEXT requires DXF R2000')
        dxfattribs = dict(dxfattribs or {})
        mtext: 'MText' = self.new_entity('MTEXT', dxfattribs)
        mtext.text = str(text)
        return mtext

    def add_ray(self, start: 'Vertex', unit_vector: 'Vertex',
                dxfattribs: dict = None) -> 'Ray':
        """
        Add a :class:`~ezdxf.entities.Ray` that begins at `start` point and
        continues to infinity (construction line). (requires DXF R2000)

        Args:
            start: location 3D point in :ref:`WCS`
            unit_vector: 3D vector (x, y, z)
            dxfattribs: additional DXF attributes

        """
        if self.dxfversion < DXF2000:
            raise DXFVersionError('RAY requires DXF R2000')
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['start'] = Vector(start)
        dxfattribs['unit_vector'] = Vector(unit_vector).normalize()
        return self.new_entity('RAY', dxfattribs)

    def add_xline(self, start: 'Vertex', unit_vector: 'Vertex',
                  dxfattribs: dict = None) -> 'XLine':
        """
        Add an infinity :class:`~ezdxf.entities.XLine` (construction line).
        (requires DXF R2000)

        Args:
            start: location 3D point in :ref:`WCS`
            unit_vector: 3D vector ``(x, y, z)``
            dxfattribs: additional DXF attributes

        """
        if self.dxfversion < DXF2000:
            raise DXFVersionError('XLINE requires DXF R2000')
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['start'] = Vector(start)
        dxfattribs['unit_vector'] = Vector(unit_vector).normalize()
        return self.new_entity('XLINE', dxfattribs)

    def add_spline(self, fit_points: Iterable['Vertex'] = None, degree: int = 3,
                   dxfattribs: dict = None) -> 'Spline':
        """
        Add a B-spline (:class:`~ezdxf.entities.Spline` entity) defined by fit
        points - the control points and knot values are created by the CAD
        application, therefore it is not predictable how the rendered spline
        will look like, because for every set of fit points exists an infinite
        set of B-splines. If `fit_points` is ``None``, an 'empty' spline will
        be created, all data has to be set by the user. (requires DXF R2000)

        AutoCAD creates a spline through fit points by a proprietary algorithm.
        `ezdxf` can not reproduce the control point calculation. See also:
        :ref:`tut_spline`.

        Args:
            fit_points: iterable of fit points as ``(x, y[, z])`` in :ref:`WCS`,
                create 'empty' :class:`~ezdxf.entities.Spline` if ``None``
            degree: degree of B-spline
            dxfattribs: additional DXF attributes

        """
        if self.dxfversion < DXF2000:
            raise DXFVersionError('SPLINE requires DXF R2000')
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['degree'] = int(degree)
        spline = self.new_entity('SPLINE', dxfattribs)  # type: Spline
        if fit_points is not None:
            spline.fit_points = Vector.generate(fit_points)
        return spline

    def add_spline_control_frame(self, fit_points: Iterable['Vertex'],
                                 degree: int = 3, method: str = 'chord',
                                 dxfattribs: dict = None) -> 'Spline':
        """
        Add a :class:`~ezdxf.entities.Spline` entity passing through given fit
        points by global B-spline interpolation, the new SPLINE entity is
        defined by a control frame and not by the fit points.

        - "uniform": creates a uniform t vector, from 0 to 1 evenly spaced, see
          `uniform`_ method
        - "distance", "chord": creates a t vector with values proportional to
          the fit point distances, see `chord length`_ method
        - "centripetal", "sqrt_chord": creates a t vector with values
          proportional to the fit point sqrt(distances), see `centripetal`_ method
        - "arc": creates a t vector with values proportional to the arc length
          between fit points.

        Args:
            fit_points: iterable of fit points as (x, y[, z]) in :ref:`WCS`
            degree: degree of B-spline
            method: calculation method for parameter vector t
            dxfattribs: additional DXF attributes

        """
        bspline = global_bspline_interpolation(fit_points, degree=degree,
                                               method=method)
        return self.add_open_spline(
            control_points=bspline.control_points,
            degree=bspline.degree,
            knots=bspline.knot_values(),
            dxfattribs=dxfattribs,
        )

    def add_open_spline(self, control_points: Iterable['Vertex'],
                        degree: int = 3, knots: Iterable[float] = None,
                        dxfattribs: dict = None) -> 'Spline':
        """
        Add an open uniform :class:`~ezdxf.entities.Spline` defined by
        `control_points`. (requires DXF R2000)

        Open uniform B-splines start and end at your first and last control point.

        Args:
            control_points: iterable of 3D points in :ref:`WCS`
            degree: degree of B-spline
            knots: knot values as iterable of floats
            dxfattribs: additional DXF attributes

        """
        spline = self.add_spline(dxfattribs=dxfattribs)
        spline.set_open_uniform(list(control_points), degree)
        if knots is not None:
            spline.knots = knots
        return spline

    def add_closed_spline(self, control_points: Iterable['Vertex'],
                          degree: int = 3, knots: Iterable[float] = None,
                          dxfattribs: dict = None) -> 'Spline':
        """
        Add a closed uniform :class:`~ezdxf.entities.Spline` defined by
        `control_points`. (requires DXF R2000)

        Closed uniform B-splines is a closed curve start and end at the first
        control point.

        Args:
            control_points: iterable of 3D points in :ref:`WCS`
            degree: degree of B-spline
            knots: knot values as iterable of floats
            dxfattribs: additional DXF attributes

        """
        spline = self.add_spline(dxfattribs=dxfattribs)
        spline.set_closed(list(control_points), degree)
        if knots is not None:
            spline.knots = knots
        return spline

    def add_rational_spline(self, control_points: Iterable['Vertex'],
                            weights: Sequence[float], degree: int = 3,
                            knots: Iterable[float] = None,
                            dxfattribs: dict = None) -> 'Spline':
        """
        Add an open rational uniform :class:`~ezdxf.entities.Spline` defined by
        `control_points`. (requires DXF R2000)

        `weights` has to be an iterable of floats, which defines the influence
        of the associated control point to the shape of the B-spline, therefore
        for each control point is one weight value required.

        Open rational uniform B-splines start and end at the first and last
        control point.

        Args:
            control_points: iterable of 3D points in :ref:`WCS`
            weights: weight values as iterable of floats
            degree: degree of B-spline
            knots: knot values as iterable of floats
            dxfattribs: additional DXF attributes

        """
        spline = self.add_spline(dxfattribs=dxfattribs)
        spline.set_open_rational(list(control_points), weights, degree)
        if knots is not None:
            spline.knots = knots
        return spline

    def add_closed_rational_spline(self, control_points: Iterable['Vertex'],
                                   weights: Sequence[float], degree: int = 3,
                                   knots: Iterable[float] = None,
                                   dxfattribs: dict = None) -> 'Spline':
        """
        Add a closed rational uniform :class:`~ezdxf.entities.Spline` defined by
        `control_points`. (requires DXF R2000)

        `weights` has to be an iterable of floats, which defines the influence
        of the associated control point to the shape of the B-spline, therefore
        for each control point is one weight value required.

        Closed rational uniform B-splines start and end at the first control point.

        Args:
            control_points: iterable of 3D points in :ref:`WCS`
            weights: weight values as iterable of floats
            degree: degree of B-spline
            knots: knot values as iterable of floats
            dxfattribs: additional DXF attributes

        """
        spline = self.add_spline(dxfattribs=dxfattribs)
        spline.set_closed_rational(list(control_points), weights, degree)
        if knots is not None:
            spline.knots = knots
        return spline

    def add_body(self, acis_data: str = None,
                 dxfattribs: dict = None) -> 'Body':
        """
        Add a :class:`~ezdxf.entities.Body` entity. (requires DXF R2000)

        Args:
            acis_data: ACIS data as iterable of text lines as strings, no
                interpretation by ezdxf possible
            dxfattribs: additional DXF attributes

        """
        return self._add_acis_entiy('BODY', acis_data, dxfattribs)

    def add_region(self, acis_data: str = None,
                   dxfattribs: dict = None) -> 'Region':
        """
        Add a :class:`~ezdxf.entities.Region` entity. (requires DXF R2000)

        Args:
            acis_data: ACIS data as iterable of text lines as strings,
                no interpretation by ezdxf possible
            dxfattribs: additional DXF attributes

        """
        return cast('Region',
                    self._add_acis_entiy('REGION', acis_data, dxfattribs))

    def add_3dsolid(self, acis_data: str = None,
                    dxfattribs: dict = None) -> 'Solid3d':
        """
        Add a 3DSOLID entity (:class:`~ezdxf.entities.Solid3d`).
        (requires DXF R2000)

        Args:
            acis_data: ACIS data as iterable of text lines as strings,
                no interpretation by ezdxf possible
            dxfattribs: additional DXF attributes

        """
        return cast('Solid3d',
                    self._add_acis_entiy('3DSOLID', acis_data, dxfattribs))

    def add_surface(self, acis_data: str = None,
                    dxfattribs: dict = None) -> 'Surface':
        """
        Add a :class:`~ezdxf.entities.Surface` entity. (requires DXF R2007)

        Args:
            acis_data: ACIS data as iterable of text lines as strings,
                no interpretation by ezdxf possible
            dxfattribs: additional DXF attributes

        """
        if self.dxfversion < DXF2007:
            raise DXFVersionError('SURFACE requires DXF R2007')
        return cast('Surface',
                    self._add_acis_entiy('SURFACE', acis_data, dxfattribs))

    def add_extruded_surface(self, acis_data: str = None,
                             dxfattribs: dict = None) -> 'ExtrudedSurface':
        """
        Add a :class:`~ezdxf.entities.ExtrudedSurface` entity.
        (requires DXF R2007)

        Args:
            acis_data: ACIS data as iterable of text lines as strings,
                no interpretation by ezdxf possible
            dxfattribs: additional DXF attributes

        """
        if self.dxfversion < DXF2007:
            raise DXFVersionError('EXTRUDEDSURFACE requires DXF R2007')
        return cast('ExtrudedSurface',
                    self._add_acis_entiy('EXTRUDEDSURFACE', acis_data,
                                         dxfattribs))

    def add_lofted_surface(self, acis_data: str = None,
                           dxfattribs: dict = None) -> 'LoftedSurface':
        """
        Add a :class:`~ezdxf.entities.LoftedSurface` entity.
        (requires DXF R2007)

        Args:
            acis_data: ACIS data as iterable of text lines as strings,
                no interpretation by ezdxf possible
            dxfattribs: additional DXF attributes

        """
        if self.dxfversion < DXF2007:
            raise DXFVersionError('LOFTEDSURFACE requires DXF R2007')
        return cast('LoftedSurface',
                    self._add_acis_entiy('LOFTEDSURFACE', acis_data,
                                         dxfattribs))

    def add_revolved_surface(self, acis_data: str = None,
                             dxfattribs: dict = None) -> 'RevolvedSurface':
        """
        Add a :class:`~ezdxf.entities.RevolvedSurface` entity.
        (requires DXF R2007)

        Args:
            acis_data: ACIS data as iterable of text lines as strings,
                no interpretation by ezdxf possible
            dxfattribs: additional DXF attributes

        """
        if self.dxfversion < DXF2007:
            raise DXFVersionError('REVOLVEDSURFACE requires DXF R2007')
        return cast('RevolvedSurface',
                    self._add_acis_entiy('REVOLVEDSURFACE', acis_data,
                                         dxfattribs))

    def add_swept_surface(self, acis_data: str = None,
                          dxfattribs: dict = None) -> 'SweptSurface':
        """
        Add a :class:`~ezdxf.entities.SweptSurface` entity.
        (requires DXF R2007)

        Args:
            acis_data: ACIS data as iterable of text lines as strings,
                no interpretation by ezdxf possible
            dxfattribs: additional DXF attributes

        """
        if self.dxfversion < DXF2007:
            raise DXFVersionError('SWEPTSURFACE requires DXF R2007')
        return cast('SweptSurface',
                    self._add_acis_entiy('SWEPTSURFACE', acis_data, dxfattribs))

    def _add_acis_entiy(self, name, acis_data: str, dxfattribs: dict) -> 'Body':
        if self.dxfversion < DXF2000:
            raise DXFVersionError(f'{name} requires DXF R2000')
        dxfattribs = dict(dxfattribs or {})
        entity = cast('Body', self.new_entity(name, dxfattribs))
        if acis_data is not None:
            entity.acis_data = acis_data
        return entity

    def add_hatch(self, color: int = 7, dxfattribs: dict = None) -> 'Hatch':
        """
        Add a :class:`~ezdxf.entities.Hatch` entity. (requires DXF R2007)

        Args:
            color: ACI (AutoCAD Color Index), default is ``7`` (black/white).
            dxfattribs: additional DXF attributes

        """
        if self.dxfversion < DXF2000:
            raise DXFVersionError('HATCH requires DXF R2000')
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['solid_fill'] = 1
        dxfattribs['color'] = int(color)
        dxfattribs['pattern_name'] = 'SOLID'
        return self.new_entity('HATCH', dxfattribs)

    def add_mesh(self, dxfattribs: dict = None) -> 'Mesh':
        """
        Add a :class:`~ezdxf.entities.Mesh` entity. (requires DXF R2007)

        Args:
            dxfattribs: additional DXF attributes

        """
        if self.dxfversion < DXF2000:
            raise DXFVersionError('MESH requires DXF R2000')
        dxfattribs = dict(dxfattribs or {})
        return self.new_entity('MESH', dxfattribs)

    def add_image(self, image_def: 'ImageDef', insert: 'Vertex',
                  size_in_units: Tuple[float, float],
                  rotation: float = 0.,
                  dxfattribs: dict = None) -> 'Image':
        """
        Add an :class:`~ezdxf.entities.Image` entity, requires a
        :class:`~ezdxf.entities.ImageDef` entity, see :ref:`tut_image`.
        (requires DXF R2000)

        Args:
            image_def: required image definition as :class:`~ezdxf.entities.ImageDef`
            insert: insertion point as 3D point in :ref:`WCS`
            size_in_units: size as ``(x, y)`` tuple in drawing units
            rotation: rotation angle around the extrusion axis, default is the
                z-axis, in degrees
            dxfattribs: additional DXF attributes

        """

        def to_vector(units_per_pixel, angle_in_rad):
            x = math.cos(angle_in_rad) * units_per_pixel
            y = math.sin(angle_in_rad) * units_per_pixel
            # supports only images in the xy-plane:
            return Vector(round(x, 6), round(y, 6), 0)

        if self.dxfversion < DXF2000:
            raise DXFVersionError('IMAGE requires DXF R2000')
        dxfattribs = dict(dxfattribs or {})
        x_pixels, y_pixels = image_def.dxf.image_size.vec2
        x_units, y_units = size_in_units
        x_units_per_pixel = x_units / x_pixels
        y_units_per_pixel = y_units / y_pixels
        x_angle_rad = math.radians(rotation)
        y_angle_rad = x_angle_rad + (math.pi / 2.)

        dxfattribs['insert'] = Vector(insert)
        dxfattribs['u_pixel'] = to_vector(x_units_per_pixel, x_angle_rad)
        dxfattribs['v_pixel'] = to_vector(y_units_per_pixel, y_angle_rad)
        dxfattribs['image_def_handle'] = image_def.dxf.handle
        dxfattribs['image_size'] = image_def.dxf.image_size
        # Creating an ImageReactor and linking it to the Image and the ImageDef
        # entity is done by adding the new Image to a layout.
        return cast('Image', self.new_entity('IMAGE', dxfattribs))

    def add_wipeout(self, vertices: Iterable['Vertex'],
                    dxfattribs: dict = None) -> 'Wipeout':
        """ Add a :class:`ezdxf.entities.Wipeout` entity, the masking area is
        defined by WCS `vertices`.

        This method creates only a 2D entity in the xy-plane of the layout,
        the z-axis of the input vertices are ignored.

        """
        wipeout = cast('Wipeout',
                       self.new_entity('WIPEOUT', dxfattribs=dxfattribs))
        wipeout.set_masking_area(vertices)
        doc = self.doc
        if doc and ('ACAD_WIPEOUT_VARS' not in doc.rootdict):
            doc.set_wipeout_variables(frame=0)
        return wipeout

    def add_underlay(self, underlay_def: 'UnderlayDef',
                     insert: 'Vertex' = (0, 0, 0),
                     scale=(1, 1, 1), rotation: float = 0.,
                     dxfattribs: dict = None) -> 'Underlay':
        """
        Add an :class:`~ezdxf.entities.Underlay` entity, requires a
        :class:`~ezdxf.entities.UnderlayDef` entity, see :ref:`tut_underlay`.
        (requires DXF R2000)

        Args:
            underlay_def: required underlay definition as :class:`~ezdxf.entities.UnderlayDef`
            insert: insertion point as 3D point in :ref:`WCS`
            scale:  underlay scaling factor as ``(x, y, z)`` tuple or as single
                value for uniform scaling for x, y and z
            rotation: rotation angle around the extrusion axis, default is the
                z-axis, in degrees
            dxfattribs: additional DXF attributes

        """
        if self.dxfversion < DXF2000:
            raise DXFVersionError('UNDERLAY requires DXF R2000')
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['insert'] = Vector(insert)
        dxfattribs['underlay_def_handle'] = underlay_def.dxf.handle
        dxfattribs['rotation'] = float(rotation)

        underlay = cast('Underlay', self.new_entity(
            underlay_def.entity_name, dxfattribs
        ))
        underlay.scaling = scale
        underlay_def.append_reactor_handle(underlay.dxf.handle)
        return underlay

    def _save_dimstyle(self, name: str) -> str:
        if name in self.doc.dimstyles:
            return name
        logger.debug(
            f'Replacing undefined DIMSTYLE "{name}" by "Standard" DIMSTYLE.')
        return 'Standard'

    def add_linear_dim(self,
                       base: 'Vertex',
                       p1: 'Vertex',
                       p2: 'Vertex',
                       location: 'Vertex' = None,
                       text: str = "<>",
                       angle: float = 0,
                       # 0=horizontal, 90=vertical, else=rotated
                       text_rotation: float = None,
                       dimstyle: str = 'EZDXF',
                       override: dict = None,
                       dxfattribs: dict = None) -> 'DimStyleOverride':
        """
        Add horizontal, vertical and rotated :class:`~ezdxf.entities.Dimension`
        line. If an :class:`~ezdxf.math.UCS` is used for dimension line rendering,
        all point definitions in UCS coordinates, translation into :ref:`WCS`
        and :ref:`OCS` is done by the rendering function. Extrusion vector is
        defined by UCS or ``(0, 0, 1)`` by default.
        See also: :ref:`tut_linear_dimension`

        This method returns a :class:`~ezdxf.entities.DimStyleOverride` object -
        to create the necessary dimension geometry, you have to call
        :meth:`~ezdxf.entities.DimStyleOverride.render` manually, this two step
        process allows additional processing steps on the
        :class:`~ezdxf.entities.Dimension` entity between creation and rendering.

        .. note::

            `ezdxf` ignores some DIMSTYLE variables, so render results may differ
            from BricsCAD or AutoCAD.

        Args:
            base: location of dimension line, any point on the dimension line or
                its extension will do (in UCS)
            p1: measurement point 1 and start point of extension line 1 (in UCS)
            p2: measurement point 2 and start point of extension line 2 (in UCS)
            location: user defined location for text mid point (in UCS)
            text: ``None`` or ``"<>"`` the measurement is drawn as text,
                ``" "`` (one space) suppresses the dimension text, everything
                else `text` is drawn as dimension text
            dimstyle: dimension style name (:class:`~ezdxf.entities.DimStyle`
                table entry), default is ``'EZDXF'``
            angle: angle from ucs/wcs x-axis to dimension line in degrees
            text_rotation: rotation angle of the dimension text as absolute
                angle (x-axis=0, y-axis=90) in degrees
            override: :class:`~ezdxf.entities.DimStyleOverride` attributes
            dxfattribs: additional DXF attributes for
                :class:`~ezdxf.entities.Dimension` entity

        Returns: :class:`~ezdxf.entities.DimStyleOverride`

        """
        type_ = {'dimtype': const.DIM_LINEAR | const.DIM_BLOCK_EXCLUSIVE}
        dimline = cast('Dimension',
                       self.new_entity('DIMENSION', dxfattribs=type_))
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['dimstyle'] = self._save_dimstyle(dimstyle)
        dxfattribs['defpoint'] = Vector(base)  # group code 10
        dxfattribs['text'] = str(text)
        dxfattribs['defpoint2'] = Vector(p1)  # group code 13
        dxfattribs['defpoint3'] = Vector(p2)  # group code 14
        dxfattribs['angle'] = float(angle)

        # text_rotation ALWAYS overrides implicit angles as absolute angle
        # (x-axis=0, y-axis=90)!
        if text_rotation is not None:
            dxfattribs['text_rotation'] = float(text_rotation)
        dimline.update_dxf_attribs(dxfattribs)

        style = DimStyleOverride(dimline, override=override)
        if location is not None:
            # special version, just for linear dimension
            style.set_location(location, leader=False, relative=False)
        return style

    def add_multi_point_linear_dim(self,
                                   base: 'Vertex',
                                   points: Iterable['Vertex'],
                                   angle: float = 0,
                                   ucs: 'UCS' = None,
                                   avoid_double_rendering: bool = True,
                                   dimstyle: str = 'EZDXF',
                                   override: dict = None,
                                   dxfattribs: dict = None,
                                   discard=False) -> None:
        """
        Add multiple linear dimensions for iterable `points`. If an
        :class:`~ezdxf.math.UCS` is used for dimension line rendering, all point
        definitions in UCS coordinates, translation into :ref:`WCS` and
        :ref:`OCS` is done by the rendering function. Extrusion vector is
        defined by UCS or ``(0, 0, 1)`` by default. See also:
        :ref:`tut_linear_dimension`

        This method sets many design decisions by itself, the necessary geometry
        will be generated automatically, no required nor possible
        :meth:`~ezdxf.entities.DimStyleOverride.render` call.
        This method is easy to use but you get what you get.

        .. note::

            `ezdxf` ignores some DIMSTYLE variables, so render results may
            differ from BricsCAD or AutoCAD.

        Args:
            base: location of dimension line, any point on the dimension line
                or its extension will do (in UCS)
            points: iterable of measurement points (in UCS)
            angle: angle from ucs/wcs x-axis to dimension line in degrees
                (``0`` = horizontal, ``90`` = vertical)
            ucs: user defined coordinate system
            avoid_double_rendering: suppresses the first extension line and the
                first arrow if possible for continued dimension entities
            dimstyle: dimension style name (DimStyle table entry),
                default is ``'EZDXF'``
            override: :class:`~ezdxf.entities.DimStyleOverride` attributes
            dxfattribs: additional DXF attributes for :class:`~ezdxf.entities.Dimension`
                entity
            discard: discard rendering result for friendly CAD applications like
                BricsCAD to get a native and likely better rendering result.
                (does not work with AutoCAD)

        """
        multi_point_linear_dimension(
            cast('GenericLayoutType', self),
            base=base,
            points=points,
            angle=angle,
            ucs=ucs,
            avoid_double_rendering=avoid_double_rendering,
            dimstyle=dimstyle,
            override=override,
            dxfattribs=dxfattribs,
            discard=discard,
        )

    def add_aligned_dim(self,
                        p1: 'Vertex',
                        p2: 'Vertex',
                        distance: float,
                        text: str = "<>",
                        dimstyle: str = 'EZDXF',
                        override: dict = None,
                        dxfattribs: dict = None) -> 'DimStyleOverride':
        """
        Add linear dimension aligned with measurement points `p1` and `p2`. If
        an :class:`~ezdxf.math.UCS` is used for dimension line rendering, all
        point definitions in UCS coordinates, translation into :ref:`WCS`
        and :ref:`OCS` is done by the rendering function. Extrusion vector
        is defined by UCS or ``(0, 0, 1)`` by default.
        See also: :ref:`tut_linear_dimension`

        This method returns a :class:`~ezdxf.entities.DimStyleOverride` object,
        to create the necessary dimension geometry, you have to  call
        :meth:`DimStyleOverride.render` manually, this two step process allows
        additional processing steps on the  :class:`~ezdxf.entities.Dimension`
        entity between creation and rendering.

        .. note::

            `ezdxf` ignores some DIMSTYLE variables, so render results may
            differ from BricsCAD or AutoCAD.

        Args:
            p1: measurement point 1 and start point of extension line 1 (in UCS)
            p2: measurement point 2 and start point of extension line 2 (in UCS)
            distance: distance of dimension line from measurement points
            text: None or "<>" the measurement is drawn as text, " " (one space)
                suppresses the dimension text, everything else `text` is drawn
                as dimension text
            dimstyle: dimension style name (:class:`~ezdxf.entities.DimStyle`
                table entry), default is ``'EZDXF'``
            override: :class:`~ezdxf.entities.DimStyleOverride` attributes
            dxfattribs: DXF attributes for :class:`~ezdxf.entities.Dimension`
                entity

        Returns: :class:`~ezdxf.entities.DimStyleOverride`

        """
        p1 = Vector(p1)
        p2 = Vector(p2)
        direction = p2 - p1
        angle = direction.angle_deg
        base = direction.orthogonal().normalize(distance) + p1
        return self.add_linear_dim(
            base=base,
            p1=p1,
            p2=p2,
            dimstyle=dimstyle,
            text=text,
            angle=angle,
            override=override,
            dxfattribs=dxfattribs,
        )

    def add_angular_dim(self,
                        base: 'Vertex',
                        line1: Tuple['Vertex', 'Vertex'],
                        line2: Tuple['Vertex', 'Vertex'],
                        location: 'Vertex' = None,
                        text: str = "<>",
                        text_rotation: float = None,
                        dimstyle: str = 'EZDXF',
                        override: dict = None,
                        dxfattribs: dict = None) -> 'DimStyleOverride':
        """
        Add angular :class:`~ezdxf.entities.Dimension` from 2 lines.
        If an :class:`~ezdxf.math.UCS` is used for angular dimension rendering,
        all point definitions in UCS coordinates, translation into :ref:`WCS`
        and :ref:`OCS` is done by the rendering function. Extrusion vector is
        defined by UCS or ``(0, 0, 1)`` by default.

        This method returns a :class:`~ezdxf.entities.DimStyleOverride` object -
        to create the necessary dimension geometry, you have to call
        :meth:`~ezdxf.entities.DimStyleOverride.render` manually, this two step
        process allows additional processing steps on the
        :class:`~ezdxf.entities.Dimension` entity between creation and rendering.

        .. note::

            `ezdxf` ignores some DIMSTYLE variables, so render results may
            differ from BricsCAD or AutoCAD.

        Args:
            base: location of dimension line, any point on the dimension line or
                its extension will do (in UCS)
            line1: specifies start leg of the angle (start point, end point) and
                determines extension line 1 (in UCS)
            line2: specifies end leg of the angle (start point, end point) and
                determines extension line 2 (in UCS)
            location: user defined location for text mid point (in UCS)
            text: ``None`` or ``"<>"`` the measurement is drawn as text, ``" "``
                (one space) suppresses the dimension text, everything else
                `text` is drawn as dimension text
            text_rotation: rotation angle of the dimension text as absolute
                angle (x-axis=0, y-axis=90) in degrees
            dimstyle: dimension style name (:class:`~ezdxf.entities.DimStyle`
                table entry), default is ``'EZDXF'``
            override: :class:`~ezdxf.entities.DimStyleOverride` attributes
            dxfattribs: additional DXF attributes for
                :class:`~ezdxf.entities.Dimension` entity

        Returns: :class:`~ezdxf.entities.DimStyleOverride`

        (not implemented yet!)

        """
        type_ = {'dimtype': const.DIM_ANGULAR | const.DIM_BLOCK_EXCLUSIVE}
        dimline = cast('Dimension',
                       self.new_entity('DIMENSION', dxfattribs=type_).cast())

        dxfattribs = dict(dxfattribs or {})
        dxfattribs['dimstyle'] = self._save_dimstyle(dimstyle)
        dxfattribs['text'] = str(text)

        dxfattribs['defpoint2'] = Vector(line1[0])  # group code 13
        dxfattribs['defpoint3'] = Vector(line1[1])  # group code 14
        dxfattribs['defpoint4'] = Vector(line2[0])  # group code 15
        dxfattribs['defpoint'] = Vector(line2[1])  # group code 10
        dxfattribs['defpoint5'] = Vector(base)  # group code 16

        # text_rotation ALWAYS overrides implicit angles as absolute angle (x-axis=0, y-axis=90)!
        if text_rotation is not None:
            dxfattribs['text_rotation'] = float(text_rotation)

        dimline.update_dxf_attribs(dxfattribs)
        style = DimStyleOverride(dimline, override=override)
        if location is not None:
            style.user_location_override(location)
        return style

    def add_angular_3p_dim(self,
                           base: 'Vertex',
                           center: 'Vertex',
                           p1: 'Vertex',
                           p2: 'Vertex',
                           location: 'Vertex' = None,
                           text: str = "<>",
                           text_rotation: float = None,
                           dimstyle: str = 'EZDXF',
                           override: dict = None,
                           dxfattribs: dict = None) -> 'DimStyleOverride':
        """
        Add angular :class:`~ezdxf.entities.Dimension` from 3 points
        (center, p1, p2).
        If an :class:`~ezdxf.math.UCS` is used for angular dimension rendering,
        all point definitions in UCS coordinates, translation into :ref:`WCS`
        and :ref:`OCS` is done by the rendering function. Extrusion vector is
        defined by UCS or ``(0, 0, 1)`` by default.

        This method returns a :class:`~ezdxf.entities.DimStyleOverride` object -
        to create the necessary dimension geometry, you have to call
        :meth:`~ezdxf.entities.DimStyleOverride.render` manually, this two step
        process allows additional processing steps on the
        :class:`~ezdxf.entities.Dimension` entity between creation and rendering.

        .. note::

            `ezdxf` ignores some DIMSTYLE variables, so render results may
            differ from BricsCAD or AutoCAD.

        Args:
            base: location of dimension line, any point on the dimension line
                or its extension will do (in UCS)
            center: specifies the vertex of the angle
            p1: specifies start leg of the angle (center -> p1) and end point
                of extension line 1 (in UCS)
            p2: specifies end leg of the  angle (center -> p2) and end point
                of extension line 2 (in UCS)
            location: user defined location for text mid point (in UCS)
            text: ``None`` or ``"<>"`` the measurement is drawn as text, ``" "``
                (one space) suppresses the dimension text, everything else
                `text` is drawn as dimension text
            text_rotation: rotation angle of the dimension text as absolute
                angle (x-axis=0, y-axis=90) in degrees
            dimstyle: dimension style name (:class:`~ezdxf.entities.DimStyle`
                table entry), default is ``'EZDXF'``
            override: :class:`~ezdxf.entities.DimStyleOverride` attributes
            dxfattribs: additional DXF attributes for
                :class:`~ezdxf.entities.Dimension` entity

        Returns: :class:`~ezdxf.entities.DimStyleOverride`

        (not implemented yet!)

        """
        type_ = {'dimtype': const.DIM_ANGULAR_3P | const.DIM_BLOCK_EXCLUSIVE}
        dimline = cast('Dimension',
                       self.new_entity('DIMENSION', dxfattribs=type_))
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['dimstyle'] = self._save_dimstyle(dimstyle)
        dxfattribs['text'] = str(text)
        dxfattribs['defpoint'] = Vector(base)
        dxfattribs['defpoint2'] = Vector(p1)
        dxfattribs['defpoint3'] = Vector(p2)
        dxfattribs['defpoint4'] = Vector(center)

        # text_rotation ALWAYS overrides implicit angles as absolute angle
        # (x-axis=0, y-axis=90)!
        if text_rotation is not None:
            dxfattribs['text_rotation'] = float(text_rotation)

        dimline.update_dxf_attribs(dxfattribs)
        style = DimStyleOverride(dimline, override=override)
        if location is not None:
            style.user_location_override(location)
        return style

    def add_diameter_dim(self,
                         center: 'Vertex',
                         mpoint: 'Vertex' = None,
                         radius: float = None,
                         angle: float = None,
                         location: 'Vertex' = None,
                         text: str = "<>",
                         dimstyle: str = 'EZ_RADIUS',
                         override: dict = None,
                         dxfattribs: dict = None) -> 'DimStyleOverride':
        """
        Add a diameter :class:`~ezdxf.entities.Dimension` line. The diameter
        dimension line requires a `center` point and a point `mpoint` on the
        circle or as an alternative a `radius` and a dimension line `angle` in
        degrees.

        If an :class:`~ezdxf.math.UCS` is used for dimension line rendering,
        all point definitions in UCS coordinates, translation into :ref:`WCS`
        and :ref:`OCS` is done by the rendering function. Extrusion vector is
        defined by UCS or ``(0, 0, 1)`` by default.

        This method returns a :class:`~ezdxf.entities.DimStyleOverride` object -
        to create the necessary dimension geometry, you have to call
        :meth:`~ezdxf.entities.DimStyleOverride.render` manually, this two step
        process allows additional processing steps on the :class:`~ezdxf.entities.Dimension`
        entity between creation and rendering.

        .. note::

            `ezdxf` ignores some DIMSTYLE variables, so render results may
            differ from BricsCAD or AutoCAD.

        Args:
            center: specifies the center of the circle (in UCS)
            mpoint: specifies the measurement point on the circle (in UCS)
            radius: specify radius, requires argument `angle`, overrides `p1` argument
            angle: specify angle of dimension line in degrees, requires argument
                `radius`, overrides `p1` argument
            location: user defined location for text mid point (in UCS)
            text: ``None`` or ``"<>"`` the measurement is drawn as text, ``" "``
                (one space) suppresses the dimension text, everything else
                `text` is drawn as dimension text
            dimstyle: dimension style name (:class:`~ezdxf.entities.DimStyle`
                table entry), default is ``'EZ_RADIUS'``
            override: :class:`~ezdxf.entities.DimStyleOverride` attributes
            dxfattribs: additional DXF attributes for
                :class:`~ezdxf.entities.Dimension` entity

        Returns: :class:`~ezdxf.entities.DimStyleOverride`

        (not implemented yet!)

        """
        type_ = {'dimtype': const.DIM_DIAMETER | const.DIM_BLOCK_EXCLUSIVE}
        dimline = cast('Dimension',
                       self.new_entity('DIMENSION', dxfattribs=type_))
        center = Vector(center)
        if location is not None:
            if radius is None:
                raise ValueError("Argument radius is required.")
            location = Vector(location)

            # (center - location) just works as expected, but in my
            # understanding it should be: (location - center)
            radius_vec = (center - location).normalize(length=radius)
        else:  # defined by mpoint = measurement point on circle
            if mpoint is None:  # defined by radius and angle
                if angle is None:
                    raise ValueError("Argument angle or mpoint required.")
                if radius is None:
                    raise ValueError("Argument radius or mpoint required.")
                radius_vec = Vector.from_deg_angle(angle, radius)
            else:
                radius_vec = Vector(mpoint) - center

        p1 = center + radius_vec
        p2 = center - radius_vec
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['dimstyle'] = self._save_dimstyle(dimstyle)
        dxfattribs['defpoint'] = Vector(p1)  # group code 10
        dxfattribs['defpoint4'] = Vector(p2)  # group code 15
        dxfattribs['text'] = str(text)

        dimline.update_dxf_attribs(dxfattribs)

        style = DimStyleOverride(dimline, override=override)
        if location is not None:
            style.user_location_override(location)
        return style

    def add_diameter_dim_2p(self,
                            p1: 'Vertex',
                            p2: 'Vertex',
                            text: str = "<>",
                            dimstyle: str = 'EZ_RADIUS',
                            override: dict = None,
                            dxfattribs: dict = None) -> 'DimStyleOverride':
        """
        Shortcut method to create a diameter dimension by two points on the
        circle and the measurement text at the default location defined by the
        associated `dimstyle`, for further information see general method
        :func:`add_diameter_dim`. Center point of the virtual circle is the
        mid point between `p1` and `p2`.

        - dimstyle ``'EZ_RADIUS'``: places the dimension text outside
        - dimstyle ``'EZ_RADIUS_INSIDE'``: places the dimension text inside

        Args:
            p1: first point of the circle (in UCS)
            p2: second point on the opposite side of the center point of the
                circle (in UCS)
            text: ``None`` or ``"<>"`` the measurement is drawn as text, ``" "``
                (one space) suppresses the dimension text, everything else
                `text` is drawn as dimension text
            dimstyle: dimension style name (:class:`~ezdxf.entities.DimStyle`
                table entry), default is ``'EZ_RADIUS'``
            override: :class:`~ezdxf.entities.DimStyleOverride` attributes
            dxfattribs: additional DXF attributes for
                :class:`~ezdxf.entities.Dimension` entity

        Returns: :class:`~ezdxf.entities.DimStyleOverride`

        """
        mpoint = Vector(p1)
        center = mpoint.lerp(p2)
        return self.add_diameter_dim(center, mpoint, text=text,
                                     dimstyle=dimstyle,
                                     override=override, dxfattribs=dxfattribs)

    def add_radius_dim(self,
                       center: 'Vertex',
                       mpoint: 'Vertex' = None,
                       radius: float = None,
                       angle: float = None,
                       location: 'Vertex' = None,
                       text: str = "<>",
                       dimstyle: str = 'EZ_RADIUS',
                       override: dict = None,
                       dxfattribs: dict = None) -> 'DimStyleOverride':
        """
        Add a radius :class:`~ezdxf.entities.Dimension` line. The radius
        dimension line requires a `center` point and a point `mpoint` on the
        circle or as an alternative a `radius` and a dimension line `angle` in
        degrees. See also: :ref:`tut_radius_dimension`

        If an :class:`~ezdxf.math.UCS` is used for dimension line rendering,
        all point definitions in UCS coordinates, translation into :ref:`WCS`
        and :ref:`OCS` is done by the rendering function. Extrusion vector is
        defined by UCS or ``(0, 0, 1)`` by default.

        This method returns a :class:`~ezdxf.entities.DimStyleOverride` object -
        to create the necessary dimension geometry, you have to call
        :meth:`~ezdxf.entities.DimStyleOverride.render` manually, this two step
        process allows additional processing steps on the
        :class:`~ezdxf.entities.Dimension` entity between creation and rendering.

        Following render types are supported:

        - Default text location outside: text aligned with dimension line;
          dimension style: ``'EZ_RADIUS'``
        - Default text location outside horizontal: ``'EZ_RADIUS'`` + dimtoh=1
        - Default text location inside: text aligned with dimension line;
          dimension style: ``'EZ_RADIUS_INSIDE'``
        - Default text location inside horizontal:``'EZ_RADIUS_INSIDE'`` + dimtih=1
        - User defined text location: argument `location` != ``None``, text
          aligned with dimension line; dimension style: ``'EZ_RADIUS'``
        - User defined text location horizontal: argument `location` != ``None``,
          ``'EZ_RADIUS'`` + dimtoh=1 for text outside horizontal, ``'EZ_RADIUS'``
          + dimtih=1 for text inside horizontal

        Placing the dimension text at a user defined `location`, overrides the
        `mpoint` and the `angle` argument, but requires a given `radius`
        argument. The `location` argument does not define the exact text
        location, instead it defines the dimension line starting at `center`
        and the measurement text midpoint projected on this dimension line
        going through `location`, if text is aligned to the dimension line.
        If text is horizontal, `location` is the kink point of the dimension
        line from radial to horizontal direction.

        .. note::

            `ezdxf` ignores some DIMSTYLE variables, so render results may
            differ from BricsCAD or AutoCAD.

        Args:
            center: center point of the circle (in UCS)
            mpoint: measurement point on the circle, overrides `angle` and
                `radius` (in UCS)
            radius: radius in drawing units, requires argument `angle`
            angle: specify angle of dimension line in degrees, requires
                argument `radius`
            location: user defined dimension text location, overrides `mpoint`
                and `angle`, but requires `radius` (in UCS)
            text: ``None`` or ``"<>"`` the measurement is drawn as text, ``" "``
                (one space) suppresses the dimension text, everything else
                `text` is drawn as dimension text
            dimstyle: dimension style name (:class:`~ezdxf.entities.DimStyle`
                table entry), default is ``'EZ_RADIUS'``
            override: :class:`~ezdxf.entities.DimStyleOverride` attributes
            dxfattribs: additional DXF attributes for
                :class:`~ezdxf.entities.Dimension` entity

        Returns: :class:`~ezdxf.entities.DimStyleOverride`

        """
        type_ = {'dimtype': const.DIM_RADIUS | const.DIM_BLOCK_EXCLUSIVE}
        dimline = cast('Dimension',
                       self.new_entity('DIMENSION', dxfattribs=type_))
        center = Vector(center)
        if location is not None:
            if radius is None:
                raise ValueError("Argument radius is required.")
            location = Vector(location)
            radius_vec = (location - center).normalize(length=radius)
            mpoint = center + radius_vec
        else:  # defined by mpoint = measurement point on circle
            if mpoint is None:  # defined by radius and angle
                if angle is None:
                    raise ValueError("Argument angle or mpoint required.")
                if radius is None:
                    raise ValueError("Argument radius or mpoint required.")
                mpoint = center + Vector.from_deg_angle(angle, radius)

        dxfattribs = dict(dxfattribs or {})
        dxfattribs['dimstyle'] = self._save_dimstyle(dimstyle)
        dxfattribs['defpoint4'] = Vector(mpoint)  # group code 15
        dxfattribs['defpoint'] = Vector(center)  # group code 10
        dxfattribs['text'] = str(text)

        dimline.update_dxf_attribs(dxfattribs)

        style = DimStyleOverride(dimline, override=override)
        if location is not None:
            style.user_location_override(location)

        return style

    def add_radius_dim_2p(self,
                          center: 'Vertex',
                          mpoint: 'Vertex',
                          text: str = "<>",
                          dimstyle: str = 'EZ_RADIUS',
                          override: dict = None,
                          dxfattribs: dict = None) -> 'DimStyleOverride':
        """
        Shortcut method to create a radius dimension by center point,
        measurement point on the circle and the measurement text at the default
        location defined by the associated `dimstyle`, for further information
        see general method :func:`add_radius_dim`.

        - dimstyle ``'EZ_RADIUS'``: places the dimension text outside
        - dimstyle ``'EZ_RADIUS_INSIDE'``: places the dimension text inside

        Args:
            center: center point of the circle (in UCS)
            mpoint: measurement point on the circle (in UCS)
            text: ``None`` or ``"<>"`` the measurement is drawn as text, ``" "``
                (one space) suppresses the dimension text, everything else
                `text` is drawn as dimension text
            dimstyle: dimension style name (:class:`~ezdxf.entities.DimStyle`
                table entry), default is ``'EZ_RADIUS'``
            override: :class:`~ezdxf.entities.DimStyleOverride` attributes
            dxfattribs: additional DXF attributes for
                :class:`~ezdxf.entities.Dimension` entity

        Returns: :class:`~ezdxf.entities.DimStyleOverride`

        """
        return self.add_radius_dim(center, mpoint, text=text, dimstyle=dimstyle,
                                   override=override, dxfattribs=dxfattribs)

    def add_radius_dim_cra(self,
                           center: 'Vertex',
                           radius: float,
                           angle: float,
                           text: str = "<>",
                           dimstyle: str = 'EZ_RADIUS',
                           override: dict = None,
                           dxfattribs: dict = None) -> 'DimStyleOverride':
        """
        Shortcut method to create a radius dimension by (c)enter point,
        (r)adius and (a)ngle, the measurement text is placed at the default
        location defined by the associated `dimstyle`, for further information
        see general method :func:`add_radius_dim`.

        - dimstyle ``'EZ_RADIUS'``: places the dimension text outside
        - dimstyle ``'EZ_RADIUS_INSIDE'``: places the dimension text inside

        Args:
            center: center point of the circle (in UCS)
            radius: radius in drawing units
            angle: angle of dimension line in degrees
            text: ``None`` or ``"<>"`` the measurement is drawn as text, ``" "``
                (one space) suppresses the dimension text, everything else
                `text` is drawn as dimension text
            dimstyle: dimension style name (:class:`~ezdxf.entities.DimStyle`
                table entry), default is ``'EZ_RADIUS'``
            override: :class:`~ezdxf.entities.DimStyleOverride` attributes
            dxfattribs: additional DXF attributes for
                :class:`~ezdxf.entities.Dimension` entity

        Returns: :class:`~ezdxf.entities.DimStyleOverride`

        """
        return self.add_radius_dim(center, radius=radius, angle=angle,
                                   text=text, dimstyle=dimstyle,
                                   override=override, dxfattribs=dxfattribs)

    def add_ordinate_dim(self,
                         origin: 'Vertex',
                         feature_location: 'Vertex',
                         leader_endpoint: 'Vertex',
                         location: 'Vertex' = None,
                         text: str = "<>",
                         dimstyle: str = 'EZDXF',
                         override: dict = None,
                         dxfattribs: dict = None) -> DimStyleOverride:
        """
        Add ordinate :class:`~ezdxf.entities.Dimension` line.
        If an :class:`~ezdxf.math.UCS` is used for dimension line rendering,
        all point definitions in UCS coordinates, translation into :ref:`WCS`
        and :ref:`OCS` is done by the rendering function. Extrusion vector is
        defined by UCS or ``(0, 0, 1)`` by default.

        This method returns a :class:`~ezdxf.entities.DimStyleOverride` object -
        to create the necessary dimension geometry, you have to call
        :meth:`~ezdxf.entities.DimStyleOverride.render` manually, this two step
        process allows additional processing steps on the
        :class:`~ezdxf.entities.Dimension` entity between creation and rendering.

        .. note::

            `ezdxf` ignores some DIMSTYLE variables, so render results may
            differ from BricsCAD or AutoCAD.

        Args:
            origin: specifies the origin of the ordinate coordinate system
                (in UCS)
            feature_location: feature location in UCS
            leader_endpoint: leader endpoint in UCS
            location: user defined location for text mid point (in UCS)
            text: ``None`` or ``"<>"`` the measurement is drawn as text, ``" "``
                (one space) suppresses the dimension text, everything else
                `text` is drawn as dimension text
            dimstyle: dimension style name (:class:`~ezdxf.entities.DimStyle`
                table entry), default is ``'EZDXF'``
            override: :class:`~ezdxf.entities.DimStyleOverride` attributes
            dxfattribs: additional DXF attributes for
                :class:`~ezdxf.entities.Dimension` entity

        Returns: :class:`~ezdxf.entities.DimStyleOverride`

        (not implemented yet!)

        """
        type_ = {'dimtype': const.DIM_ORDINATE | const.DIM_BLOCK_EXCLUSIVE}
        dimline = cast('Dimension',
                       self.new_entity('DIMENSION', dxfattribs=type_))
        dxfattribs = dict(dxfattribs or {})
        dxfattribs['dimstyle'] = self._save_dimstyle(dimstyle)
        dxfattribs['defpoint'] = Vector(origin)  # group code 10
        dxfattribs['defpoint2'] = Vector(feature_location)  # group code 13
        dxfattribs['defpoint3'] = Vector(leader_endpoint)  # group code 14
        dxfattribs['text'] = str(text)
        dimline.update_dxf_attribs(dxfattribs)

        style = DimStyleOverride(dimline, override=override)
        if location is not None:
            style.user_location_override(location)
        return style

    def add_arrow(self, name: str, insert: 'Vertex', size: float = 1.,
                  rotation: float = 0,
                  dxfattribs: dict = None) -> Vector:
        return ARROWS.render_arrow(self, name=name, insert=insert, size=size,
                                   rotation=rotation, dxfattribs=dxfattribs)

    def add_arrow_blockref(self, name: str, insert: 'Vertex', size: float = 1.,
                           rotation: float = 0,
                           dxfattribs: dict = None) -> Vector:
        return ARROWS.insert_arrow(self, name=name, insert=insert, size=size,
                                   rotation=rotation, dxfattribs=dxfattribs)

    def add_leader(self,
                   vertices: Iterable['Vertex'],
                   dimstyle: str = 'EZDXF',
                   override: dict = None,
                   dxfattribs: dict = None) -> 'Leader':
        """
        The :class:`~ezdxf.entities.Leader` entity represents an arrow, made up
        of one or more vertices (or spline fit points) and an arrowhead.
        The label or other content to which the :class:`~ezdxf.entities.Leader`
        is attached is stored as a separate entity, and is not part of the
        :class:`~ezdxf.entities.Leader` itself.
        (requires DXF R2000)

        :class:`~ezdxf.entities.Leader` shares its styling infrastructure with
        :class:`~ezdxf.entities.Dimension`.

        By default a :class:`~ezdxf.entities.Leader` without any annotation is
        created. For creating more fancy leaders and annotations see
        documentation provided by Autodesk or `Demystifying DXF: LEADER and MULTILEADER
        implementation notes <https://atlight.github.io/formats/dxf-leader.html>`_  .


        Args:
            vertices: leader vertices (in :ref:`WCS`)
            dimstyle: dimension style name (:class:`~ezdxf.entities.DimStyle`
                table entry), default is ``'EZDXF'``
            override: override :class:`~ezdxf.entities.DimStyleOverride` attributes
            dxfattribs: additional DXF attributes for
                :class:`~ezdxf.entities.Leader` entity

        """

        def filter_unsupported_dimstyle_attributes(attribs: dict) -> dict:
            return {k: v for k, v in attribs.items() if
                    k not in LEADER_UNSUPPORTED_DIMSTYLE_ATTRIBS}

        if self.dxfversion < DXF2000:
            raise DXFVersionError('LEADER requires DXF R2000')

        dxfattribs = dxfattribs or {}
        dxfattribs['dimstyle'] = self._save_dimstyle(dimstyle)
        dxfattribs.setdefault('annotation_type', 3)
        leader = cast('Leader', self.new_entity('LEADER', dxfattribs))
        leader.set_vertices(vertices)
        if override:
            override = filter_unsupported_dimstyle_attributes(override)
            if 'dimldrblk' in override:
                self.doc.acquire_arrow(override['dimldrblk'])
            # Class Leader() supports the required OverrideMixin() interface
            DimStyleOverride(cast('Dimension', leader),
                             override=override).commit()
        return leader


LEADER_UNSUPPORTED_DIMSTYLE_ATTRIBS = {'dimblk', 'dimblk1', 'dimblk2'}
