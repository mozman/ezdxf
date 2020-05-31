# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-03-06
from typing import TYPE_CHECKING, Iterable, Sequence
import array
import copy
from itertools import chain
from contextlib import contextmanager
from ezdxf.math import Vector, Matrix44
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2000, DXFValueError
from ezdxf.lldxf.packedtags import VertexArray
from ezdxf.math.bspline import uniform_knot_vector, open_uniform_knot_vector, BSpline
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace, Drawing, Vertex, Tags

__all__ = ['Spline']

acdb_spline = DefSubclass('AcDbSpline', {
    # Spline flag (bit coded):
    # 1 = Closed spline
    # 2 = Periodic spline
    # 4 = Rational spline
    # 8 = Planar
    # 16 = Linear (planar bit is also set)
    'flags': DXFAttr(70, default=0),
    'degree': DXFAttr(71, default=3),
    'n_knots': DXFAttr(72, xtype=XType.callback, getter='knot_count'),
    'n_control_points': DXFAttr(73, xtype=XType.callback, getter='control_point_count'),
    'n_fit_points': DXFAttr(74, xtype=XType.callback, getter='fit_point_count'),
    'knot_tolerance': DXFAttr(42, default=1e-10, optional=True),
    'control_point_tolerance': DXFAttr(43, default=1e-10, optional=True),
    'fit_tolerance': DXFAttr(44, default=1e-10, optional=True),
    'start_tangent': DXFAttr(12, xtype=XType.point3d, optional=True),
    'end_tangent': DXFAttr(13, xtype=XType.point3d, optional=True),
    # extrusion is the normal vector (omitted if the spline is non-planar)
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0, 0, 1), optional=True),
    # 10: Control points (in WCS); one entry per control point
    # 11: Fit points (in WCS); one entry per fit point
    # 40: Knot value (one entry per knot)
    # 41: Weight (if not 1); with multiple group pairs, they are present if all are not 1
})


class SplineData:
    def __init__(self, spline: 'Spline'):
        self.fit_points = spline.fit_points
        self.control_points = spline.control_points
        self.knots = spline.knots
        self.weights = spline.weights


REMOVE_CODES = {10, 11, 40, 41, 72, 73, 74}


@register_entity
class Spline(DXFGraphic):
    """ DXF SPLINE entity """
    DXFTYPE = 'SPLINE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_spline)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000
    CLOSED = 1  # closed b-spline
    PERIODIC = 2  # uniform b-spline
    RATIONAL = 4  # rational b-spline
    PLANAR = 8  # all spline points in a plane, don't read or set this bit, just ignore like AutoCAD
    LINEAR = 16  # always set with PLANAR, don't read or set this bit, just ignore like AutoCAD

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self.fit_points = VertexArray()  # data stored as array.array('d')
        self.control_points = VertexArray()  # data stored as array.array('d')
        self.knots = []  # data stored as array.array('d')
        self.weights = []  # data stored as array.array('d')

    def _copy_data(self, entity: 'Spline') -> None:
        """ Copy data: control_points, fit_points, weights, knot_values. """
        entity._control_points = copy.deepcopy(self._control_points)
        entity._fit_points = copy.deepcopy(self._fit_points)
        entity._knots = copy.deepcopy(self._knots)
        entity._weights = copy.deepcopy(self._weights)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.find_subclass(acdb_spline.name)
            # load spline data (fit points, control points, weights, knots) and remove their tags from subclass
            self.load_spline_data(tags)
            # load remaining data into name space
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_spline)
            if len(tags):
                processor.log_unprocessed_tags(tags, subclass=acdb_spline.name)
        return dxf

    def load_spline_data(self, spline_tags: 'Tags') -> None:
        self.control_points = (value for code, value in spline_tags if code == 10)
        self.fit_points = (value for code, value in spline_tags if code == 11)
        self.knots = (value for code, value in spline_tags if code == 40)
        self.weights = (value for code, value in spline_tags if code == 41)
        spline_tags.remove_tags(codes=REMOVE_CODES)

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_spline.name)
        self.dxf.export_dxf_attribs(tagwriter, ['extrusion', 'flags', 'degree'])
        tagwriter.write_tag2(72, self.knot_count())
        tagwriter.write_tag2(73, self.control_point_count())
        tagwriter.write_tag2(74, self.fit_point_count())
        self.dxf.export_dxf_attribs(tagwriter, [
            'knot_tolerance', 'control_point_tolerance', 'fit_tolerance', 'start_tangent', 'end_tangent',
        ])

        self.export_spline_data(tagwriter)

    def export_spline_data(self, tagwriter: 'TagWriter'):
        for value in self._knots:
            tagwriter.write_tag2(40, value)

        if len(self._weights):
            for value in self._weights:
                tagwriter.write_tag2(41, value)

        self._control_points.export_dxf(tagwriter, code=10)
        self._fit_points.export_dxf(tagwriter, code=11)

    @property
    def closed(self) -> bool:
        """ ``True`` if spline is closed. A closed spline has a connection from the last control point
        to the first control point. (read/write)
        """
        return self.get_flag_state(self.CLOSED, name='flags')

    @closed.setter
    def closed(self, status: bool) -> None:
        self.set_flag_state(self.CLOSED, state=status, name='flags')

    @property
    def knots(self) -> 'array.array':  # group code 40
        """ Knot values as :code:`array.array('d')`. """
        return self._knots

    @knots.setter
    def knots(self, values: Iterable[float]) -> None:
        self._knots = array.array('d', values)

    def knot_count(self) -> int:  # DXF callback attribute Spline.dxf.n_knots
        """ Count of knot values. """
        return len(self._knots)

    @property
    def weights(self) -> 'array.array':  # group code 41
        """ Control point weights as :code:`array.array('d')`. """
        return self._weights

    @weights.setter
    def weights(self, values: Iterable[float]) -> None:
        self._weights = array.array('d', values)

    @property
    def control_points(self) -> VertexArray:  # group code 10
        """ :class:`~ezdxf.lldxf.packedtags.VertexArray` of control points in :ref:`WCS`. """
        return self._control_points

    @control_points.setter
    def control_points(self, points: Iterable['Vertex']) -> None:
        self._control_points = VertexArray(chain.from_iterable(Vector.generate(points)))

    def control_point_count(self) -> int:  # DXF callback attribute Spline.dxf.n_control_points
        """ Count of control points. """
        return len(self.control_points)

    @property
    def fit_points(self) -> VertexArray:  # group code 11
        """ :class:`~ezdxf.lldxf.packedtags.VertexArray` of fit points in :ref:`WCS`. """
        return self._fit_points

    @fit_points.setter
    def fit_points(self, points: Iterable['Vertex']) -> None:
        self._fit_points = VertexArray(chain.from_iterable(Vector.generate(points)))

    def fit_point_count(self) -> int:  # DXF callback attribute Spline.dxf.n_fit_points
        """ Count of fit points. """
        return len(self.fit_points)

    def construction_tool(self) -> BSpline:
        """
        Returns construction tool :class:`ezdxf.math.BSpline`.

        .. versionadded:: 0.13

        """
        if self.control_point_count():
            weights = self.weights if len(self.weights) else None
            knots = self.knots if len(self.knots) else None
            return BSpline(control_points=self.control_points, order=self.dxf.degree + 1, knots=knots, weights=weights)
        elif self.fit_point_count():
            return BSpline.from_fit_points(self.fit_points, degree=self.dxf.degree)
        else:
            raise ValueError('Construction tool requires control- or fit points.')

    def apply_construction_tool(self, s: BSpline) -> None:
        """
        Set SPLINE data from construction tool :class:`ezdxf.math.BSpline`.

        .. versionadded:: 0.13

        """
        self.dxf.degree = s.degree
        self.control_points = s.control_points
        self.fit_points = []  # remove fit points
        self.knots = s.knots()
        self.weights = s.weights()
        self.set_flag_state(Spline.RATIONAL, state=bool(len(self.weights)))

    def set_open_uniform(self, control_points: Sequence['Vertex'], degree: int = 3) -> None:
        """
        Open B-spline with uniform knot vector, start and end at your first and last control points.

        """
        self.dxf.flags = 0  # clear all flags
        self.dxf.degree = degree
        self.control_points = control_points
        self.knots = open_uniform_knot_vector(len(control_points), degree + 1)

    def set_uniform(self, control_points: Sequence['Vertex'], degree: int = 3) -> None:
        """
        B-spline with uniform knot vector, does NOT start and end at your first and last control points.

        """
        self.dxf.flags = 0  # clear all flags
        self.dxf.degree = degree
        self.control_points = control_points
        self.knots = uniform_knot_vector(len(control_points), degree + 1)

    def set_periodic(self, control_points: Sequence['Vertex'], degree=3) -> None:
        """
        Closed B-spline with uniform knot vector, start and end at your first control point.

        """
        self.dxf.flags = self.PERIODIC | self.CLOSED
        self.dxf.degree = degree
        self.control_points = control_points
        # AutoDesk Developer Docs:
        # If the spline is periodic, the length of knot vector will be greater than length of the control array by 1.
        self.knots = range(len(control_points) + 1)

    def set_open_rational(self, control_points: Sequence['Vertex'], weights: Sequence[float], degree: int = 3) -> None:
        """
        Open rational B-spline with uniform knot vector, start and end at your first and last control points, and has
        additional control possibilities by weighting each control point.

        """
        self.set_open_uniform(control_points, degree=degree)
        self.dxf.flags = self.dxf.flags | self.RATIONAL
        if len(weights) != len(self.control_points):
            raise DXFValueError('Control point count must be equal to weights count.')
        self.weights = weights

    def set_uniform_rational(self, control_points: Sequence['Vertex'], weights: Sequence[float],
                             degree: int = 3) -> None:
        """
        Rational B-spline with uniform knot vector, deos NOT start and end at your first and last control points, and
        has additional control possibilities by weighting each control point.

        """
        self.set_uniform(control_points, degree=degree)
        self.dxf.flags = self.dxf.flags | self.RATIONAL
        if len(weights) != len(self.control_points):
            raise DXFValueError('Control point count must be equal to weights count.')
        self.weights = weights

    def set_periodic_rational(self, control_points: Sequence['Vertex'], weights: Sequence[float],
                              degree: int = 3) -> None:
        """
        Closed rational B-spline with uniform knot vector, start and end at your first control point, and has
        additional control possibilities by weighting each control point.

        """
        self.set_periodic(control_points, degree=degree)
        self.dxf.flags = self.dxf.flags | self.RATIONAL
        if len(weights) != len(self.control_points):
            raise DXFValueError('Control point count must be equal to weights count.')
        self.weights = weights

    @contextmanager
    def edit_data(self) -> 'SplineData':
        """
        .. versionchanged:: 0.10

            This method only exist for backward compatibility, since v0.10 SPLINE attributes :attr:`fit_points`,
            :attr:`control_points`, :attr:`knots` and :attr:`weights` are read- and writeable list-like containers.

        Context manager for all spline data, returns :class:`SplineData`.

        Fit points, control points, knot values and weights can be manipulated as lists by using the general
        context manager :meth:`Spline.edit_data`::

            with spline.edit_data() as spline_data:
                # spline_data contains list like objects: add, change or delete items as you want
                # fit_points and control_points have to be (x, y, z) tuples
                # knot_values and weights have to be numbers
                spline_data.fit_points.append((200, 300, 0))  # append a fit point
                # on exit the context manager sets spline data automatically and updates all counters

        """
        data = SplineData(self)
        yield data
        if data.fit_points is not self.fit_points:
            self.fit_points = data.fit_points

        if data.control_points is not self.control_points:
            self.control_points = data.control_points

        if data.knots is not self.knots:
            self.knots = data.knots

        if data.weights is not self.weights:
            self.weights = data.weights

    def transform(self, m: 'Matrix44') -> 'Spline':
        """ Transform SPLINE entity by transformation matrix `m` inplace.

        .. versionadded:: 0.13

        """
        self._control_points.transform(m)
        self._fit_points.transform(m)
        # Transform optional attributes if they exist
        dxf = self.dxf
        for name in ('start_tangent', 'end_tangent', 'extrusion'):
            if dxf.hasattr(name):
                dxf.set(name, m.transform_direction(dxf.get(name)))

        return self
