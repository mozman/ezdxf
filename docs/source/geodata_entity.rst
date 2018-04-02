GeoData
=======

.. class:: GeoData(DXFObject)

    Introduced in DXF version R2010 (AC1024), dxftype is GEODATA

    The GEODATA entity is associated to the :class:`Modelspace` object, create new geo data by
    :meth:`Modelspace.new_geodata`, or get existing geo data by :meth:`Modelspace.get_geodata`.

.. seealso::

    `using_geodata.py <https://github.com/mozman/ezdxf/blob/master/examples/using_geodata.py>`_

DXF Attributes for GeoData
--------------------------

.. attribute:: GeoData.dxf.version

    - 1 = 2009
    - 2 = 2010

.. attribute:: GeoData.dxf.coordinate_type

    - 0 = unknown
    - 1 = local grid
    - 2 = projected grid
    - 3 = geographic (latitude/longitude)

.. attribute:: GeoData.dxf.block_record

    Handle of host block table record.

.. attribute:: GeoData.dxf.design_point

    Reference point in WCS coordinates.

.. attribute:: GeoData.dxf.reference_point

    Reference point in coordinate system coordinates, valid only when coordinate type is Local Grid.

.. attribute:: GeoData.dxf.north_direction

    North direction as 2D vector.

.. attribute:: GeoData.dxf.horizontal_unit_scale

    Horizontal unit scale, factor which converts horizontal design coordinates to meters by multiplication.

.. attribute:: GeoData.dxf.vertical_unit_scale

    Vertical unit scale, factor which converts vertical design coordinates to meters by multiplication.

.. attribute:: GeoData.dxf.horizontal_units

    Horizontal units per UnitsValue enumeration. Will be kUnitsUndefined if units specified by horizontal
    unit scale is not supported by AutoCAD enumeration.

.. attribute:: GeoData.dxf.vertical_units

    Vertical units per UnitsValue enumeration. Will be kUnitsUndefined if units specified by vertical unit scale is not
    supported by AutoCAD enumeration.

.. attribute:: GeoData.dxf.up_direction

    Up direction as 3D vector.

.. attribute:: GeoData.dxf.scale_estimation_method

    - 1 = none
    - 2 = user specified scale factor
    - 3 = grid scale at reference point
    - 4 = prismoidal

.. attribute:: GeoData.dxf.sea_level_correction

    Bool flag specifying whether to do sea level correction.

.. attribute:: GeoData.dxf.user_scale_factor

.. attribute:: GeoData.dxf.sea_level_elevation

.. attribute:: GeoData.dxf.coordinate_projection_radius

.. attribute:: GeoData.dxf.geo_rss_tag

.. attribute:: GeoData.dxf.observation_from_tag

.. attribute:: GeoData.dxf.observation_to_tag

.. attribute:: GeoData.dxf.mesh_faces_count


GeoData Methods
---------------

.. method:: GeoData.get_coordinate_system_definition()

    :returns: Coordinate system definition string (always a XML string?)

.. method:: GeoData.set_coordinate_system_definition(text)

.. method:: GeoData.get_mesh_data()

    Returns mesh as list of vertices and list of faces.
    Each vertex entry is a 2-tuple of source and target point, vertices are 2D points.
    Each face entry is a 3-tuple of vertex indices (0 based).

    :returns: tuple (vertices, faces)

.. method:: GeoData.set_mesh_data(vertices=None, faces=None)

    Each vertex entry is a 2-tuple of source and target point, all vertices are 2D points.
    Each face entry is a 3-tuple of vertex indices (0 based), faces are optional.


