# Created: 10.03.2013
# Copyright (c) 2013-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import math
from .lldxf import const
from .lldxf.const import DXFValueError, DXFVersionError, DXFKeyError
from ezdxf.algebra import Vector
from ezdxf.algebra import bspline_control_frame, bspline_control_frame_approx


def copy_attribs(dxfattribs=None):
    if dxfattribs is None:
        result = {}
    else:
        result = dict(dxfattribs)
    return result


class GraphicsFactory(object):
    """ Abstract base class for BaseLayout()
    """
    def __init__(self, dxffactory):
        self._dxffactory = dxffactory

    @property
    def dxfversion(self):
        return self._dxffactory.dxfversion

    def build_and_add_entity(self, type_, dxfattribs):
        raise NotImplementedError("Abstract method call.")

    def add_point(self, location, dxfattribs=None):
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['location'] = location
        return self.build_and_add_entity('POINT', dxfattribs)

    def add_line(self, start, end, dxfattribs=None):
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['start'] = start
        dxfattribs['end'] = end
        return self.build_and_add_entity('LINE', dxfattribs)

    def add_circle(self, center, radius, dxfattribs=None):
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['center'] = center
        dxfattribs['radius'] = radius
        return self.build_and_add_entity('CIRCLE', dxfattribs)

    def add_arc(self, center, radius, start_angle, end_angle, dxfattribs=None):
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['center'] = center
        dxfattribs['radius'] = radius
        dxfattribs['start_angle'] = start_angle
        dxfattribs['end_angle'] = end_angle
        return self.build_and_add_entity('ARC', dxfattribs)

    def add_solid(self, points, dxfattribs=None):
        return self._add_quadrilateral('SOLID', points, dxfattribs)

    def add_trace(self, points, dxfattribs=None):
        return self._add_quadrilateral('TRACE', points, dxfattribs)

    def add_3dface(self, points, dxfattribs=None):
        return self._add_quadrilateral('3DFACE', points, dxfattribs)

    def add_text(self, text, dxfattribs=None):
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['text'] = text
        dxfattribs.setdefault('insert', (0, 0))
        return self.build_and_add_entity('TEXT', dxfattribs)

    def add_blockref(self, name, insert, dxfattribs=None):
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['name'] = name
        dxfattribs['insert'] = insert
        blockref = self.build_and_add_entity('INSERT', dxfattribs)
        return blockref

    def add_auto_blockref(self, name, insert, values, dxfattribs=None):
        def get_dxfattribs(attdef):
            dxfattribs = attdef.dxfattribs()
            dxfattribs.pop('prompt', None)
            dxfattribs.pop('handle', None)
            return dxfattribs

        def unpack(dxfattribs):
            tag = dxfattribs.pop('tag')
            text = values.get(tag, "")
            insert = dxfattribs.pop('insert')
            return tag, text, insert

        def autofill(blockref, blockdef):
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

    def add_attrib(self, tag, text, insert=(0, 0), dxfattribs=None):
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['tag'] = tag
        dxfattribs['text'] = text
        dxfattribs['insert'] = insert
        return self.build_and_add_entity('ATTRIB', dxfattribs)

    def add_polyline2d(self, points, dxfattribs=None):
        dxfattribs = copy_attribs(dxfattribs)
        closed = dxfattribs.pop('closed', False)
        polyline = self.build_and_add_entity('POLYLINE', dxfattribs)
        polyline.close(closed)
        polyline.append_vertices(points)
        return polyline

    def add_polyline3d(self, points, dxfattribs=None):
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | const.POLYLINE_3D_POLYLINE
        return self.add_polyline2d(points, dxfattribs)

    def add_polymesh(self, size=(3, 3), dxfattribs=None):
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

    def add_polyface(self, dxfattribs=None):
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | const.POLYLINE_POLYFACE
        m_close = dxfattribs.pop('m_close', False)
        n_close = dxfattribs.pop('n_close', False)
        polyface = self.build_and_add_entity('POLYLINE', dxfattribs)
        polyface.close(m_close, n_close)
        return polyface.cast()

    def _add_quadrilateral(self, type_, points, dxfattribs=None):
        dxfattribs = copy_attribs(dxfattribs)
        entity = self.build_and_add_entity(type_, dxfattribs)
        for x, point in enumerate(self._four_points(points)):
            entity[x] = point
        return entity

    @staticmethod
    def _four_points(points):
        if len(points) not in (3, 4):
            raise DXFValueError('3 or 4 points required.')
        for point in points:
            yield point
        if len(points) == 3:
            yield point  # again

    def add_shape(self, name, insert=(0, 0), size=1.0, dxfattribs=None):
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['name'] = name
        dxfattribs['insert'] = insert
        dxfattribs['size'] = size
        return self.build_and_add_entity('SHAPE', dxfattribs)

# new entities in DXF AC1015 (R2000)

    def add_lwpolyline(self, points, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('LWPOLYLINE requires DXF version R2000+')
        dxfattribs = copy_attribs(dxfattribs)
        closed = dxfattribs.pop('closed', False)
        lwpolyline = self.build_and_add_entity('LWPOLYLINE', dxfattribs)
        lwpolyline.set_points(points)
        lwpolyline.closed = closed
        return lwpolyline

    def add_ellipse(self, center, major_axis=(1, 0, 0), ratio=1, start_param=0, end_param=6.283185307, dxfattribs=None):
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

    def add_mtext(self, text, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('MTEXT requires DXF version R2000+')
        dxfattribs = copy_attribs(dxfattribs)
        mtext = self.build_and_add_entity('MTEXT', dxfattribs)
        mtext.set_text(text)
        return mtext

    def add_ray(self, start, unit_vector, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('RAY requires DXF version R2000+')
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['start'] = start
        dxfattribs['unit_vector'] = unit_vector
        return self.build_and_add_entity('RAY', dxfattribs)

    def add_xline(self, start, unit_vector, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('XLINE requires DXF version R2000+')
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['start'] = start
        dxfattribs['unit_vector'] = unit_vector
        return self.build_and_add_entity('XLINE', dxfattribs)

    def add_spline(self, fit_points=None, degree=3, dxfattribs=None):
        """
        Add a B-spline defined by fit points, the control points and knot values are created by the CAD application,
        therefor it is not predictable how the rendered spline will look like, because for every set of fit points
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

    def add_spline_control_frame(self, fit_points, degree=3, method='distance', power=.5, dxfattribs=None):
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

    def add_spline_approx(self, fit_points, count, degree=3, method='distance', power=.5, dxfattribs=None):
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

    def add_open_spline(self, control_points, degree=3, knots=None, dxfattribs=None):
        spline = self.add_spline(dxfattribs=dxfattribs)
        spline.set_open_uniform(list(control_points), degree)
        if knots is not None:
            spline.set_knot_values(list(knots))
        return spline

    def add_closed_spline(self, control_points, degree=3, knots=None, dxfattribs=None):
        spline = self.add_spline(dxfattribs=dxfattribs)
        spline.set_periodic(list(control_points), degree)
        if knots is not None:
            spline.set_knot_values(list(knots))
        return spline

    def add_rational_spline(self, control_points, weights, degree=3, knots=None, dxfattribs=None):
        spline = self.add_spline(dxfattribs=dxfattribs)
        spline.set_open_rational(list(control_points), weights, degree)
        if knots is not None:
            spline.set_knot_values(list(knots))
        return spline

    def add_closed_rational_spline(self, control_points, weights, degree=3, knots=None, dxfattribs=None):
        spline = self.add_spline(dxfattribs=dxfattribs)
        spline.set_periodic_rational(list(control_points), weights, degree)
        if knots is not None:
            spline.set_knot_values(list(knots))
        return spline

    def add_body(self, acis_data=None, dxfattribs=None):
        return self._add_acis_entiy('BODY', acis_data, dxfattribs)

    def add_region(self, acis_data=None, dxfattribs=None):
        return self._add_acis_entiy('REGION', acis_data, dxfattribs)

    def add_3dsolid(self, acis_data=None, dxfattribs=None):
        return self._add_acis_entiy('3DSOLID', acis_data, dxfattribs)

    def add_surface(self, acis_data=None, dxfattribs=None):
        return self._add_acis_entiy('SURFACE', acis_data, dxfattribs)

    def add_extruded_surface(self, acis_data=None, dxfattribs=None):
        return self._add_acis_entiy('EXTRUDEDSURFACE', acis_data, dxfattribs)

    def add_lofted_surface(self, acis_data=None, dxfattribs=None):
        return self._add_acis_entiy('LOFTEDSURFACE', acis_data, dxfattribs)

    def add_revolved_surface(self, acis_data=None, dxfattribs=None):
        return self._add_acis_entiy('REVOLVEDSURFACE', acis_data, dxfattribs)

    def add_swept_surface(self, acis_data=None, dxfattribs=None):
        return self._add_acis_entiy('SWEPTSURFACE', acis_data, dxfattribs)

    def _add_acis_entiy(self, name, acis_data, dxfattribs):
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('{} requires DXF version R2000+'.format(name))
        dxfattribs = copy_attribs(dxfattribs)
        entity = self.build_and_add_entity(name, dxfattribs)
        if acis_data is not None:
            entity.set_acis_data(acis_data)
        return entity

    def add_hatch(self, color=7, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('HATCH requires DXF version R2000+')
        dxfattribs = copy_attribs(dxfattribs)
        dxfattribs['solid_fill'] = 1
        dxfattribs['color'] = color
        dxfattribs['pattern_name'] = 'SOLID'
        return self.build_and_add_entity('HATCH', dxfattribs)

    def add_mesh(self, dxfattribs=None):
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('MESH requires DXF version R2000+')
        dxfattribs = copy_attribs(dxfattribs)
        return self.build_and_add_entity('MESH', dxfattribs)

    def add_image(self, image_def, insert, size_in_units, rotation=0., dxfattribs=None):
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

    def add_underlay(self, underlay_def, insert=(0, 0, 0), scale=(1, 1, 1), rotation=0., dxfattribs=None):
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

    def add_rotated_dim(self):
        pass

    def add_aligned_dim(self):
        pass

    def add_angular_dim(self):
        pass

    def add_diameter_dim(self):
        pass

    def add_radial_dim(self):
        pass

    def add_angular_3p_dim(self):
        pass

    def add_ordinate_dim(self):
        pass

