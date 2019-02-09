Surface
=======

.. class:: Surface(Body)

Introduced in DXF version R2007 (AC1021), dxftype is SURFACE.

A 3D object created by an ACIS based geometry kernel provided by the `Spatial Corp.`_
Create :class:`Surface` objects in layouts and blocks by factory function
:meth:`~Layout.add_surface`.

DXF Attributes for Surface
--------------------------

:ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: Surface.dxf.u_count

Number of U isolines

.. attribute:: Surface.dxf.v_count

Number of V2 isolines

Surface Methods
---------------

.. method:: Surface.get_acis_data()

Get the ACIS source code as a list of strings.

.. method:: Surface.set_acis_data(test_lines)

Set the ACIS source code as a list of strings **without** line endings.

.. method:: Surface.edit_data()

Context manager for ACIS text lines, returns :class:`ModelerGeometryData`.

.. _Spatial Corp.: http://www.spatial.com/products/3d-acis-modeling

ExtrudedSurface
===============

.. class:: ExtrudedSurface(Surface)

Introduced in DXF version R2007 (AC1021), dxftype is EXTRUDEDSURFACE.

DXF Attributes for ExtrudedSurface
----------------------------------

.. attribute:: ExtrudedSurface.dxf.class_id

.. attribute:: ExtrudedSurface.dxf.sweep_vector

.. attribute:: ExtrudedSurface.dxf.draft_angle

.. attribute:: ExtrudedSurface.dxf.draft_start_distance

.. attribute:: ExtrudedSurface.dxf.draft_end_distance

.. attribute:: ExtrudedSurface.dxf.twist_angle

.. attribute:: ExtrudedSurface.dxf.scale_factor

.. attribute:: ExtrudedSurface.dxf.align_angle

.. attribute:: ExtrudedSurface.dxf.solid

.. attribute:: ExtrudedSurface.dxf.sweep_alignment_flags

    - 0 = No alignment
    - 1 = Align sweep entity to path
    - 2 = Translate sweep entity to path
    - 3 = Translate path to sweep entity

.. attribute:: ExtrudedSurface.dxf.align_start

.. attribute:: ExtrudedSurface.dxf.bank

.. attribute:: ExtrudedSurface.dxf.base_point_set

.. attribute:: ExtrudedSurface.dxf.sweep_entity_transform_computed

.. attribute:: ExtrudedSurface.dxf.path_entity_transform_computed

.. attribute:: ExtrudedSurface.dxf.reference_vector_for_controlling_twist


ExtrudedSurface Methods
-----------------------

.. method:: ExtrudedSurface.set_transformation_matrix_extruded_entity(matrix)

    :param matrix: iterable of 16 numeric values.

.. method:: ExtrudedSurface.get_transformation_matrix_extruded_entity()

    :returns: :class:`~ezdxf.math.Matrix44` object

.. method:: ExtrudedSurface.set_sweep_entity_transformation_matrix(matrix)

    :param matrix: iterable of 16 numeric values.

.. method:: ExtrudedSurface.get_sweep_entity_transformation_matrix()

    :returns: :class:`~ezdxf.math.Matrix44` object

.. method:: ExtrudedSurface.set_path_entity_transformation_matrix(matrix)

    :param matrix: iterable of 16 numeric values.

.. method:: ExtrudedSurface.get_path_entity_transformation_matrix()

    :returns: :class:`~ezdxf.math.Matrix44` object

LoftedSurface
=============

.. class:: LoftedSurface(Surface)

Introduced in DXF version R2007 (AC1021), dxftype is LOFTEDSURFACE.

DXF Attributes for LoftedSurface
----------------------------------

.. attribute:: LoftedSurface.dxf.plane_normal_lofting_type

.. attribute:: LoftedSurface.dxf.start_draft_angle

.. attribute:: LoftedSurface.dxf.end_draft_angle

.. attribute:: LoftedSurface.dxf.start_draft_magnitude

.. attribute:: LoftedSurface.dxf.end_draft_magnitude

.. attribute:: LoftedSurface.dxf.arc_length_parameterization

.. attribute:: LoftedSurface.dxf.no_twist

.. attribute:: LoftedSurface.dxf.align_direction

.. attribute:: LoftedSurface.dxf.simple_surfaces

.. attribute:: LoftedSurface.dxf.closed_surfaces

.. attribute:: LoftedSurface.dxf.solid

.. attribute:: LoftedSurface.dxf.ruled_surface

.. attribute:: LoftedSurface.dxf.virtual_guide

LoftedSurface Methods
---------------------

.. method:: LoftedSurface.set_transformation_matrix_lofted_entity(matrix)

    :param matrix: iterable of 16 numeric values.

.. method:: LoftedSurface.get_transformation_matrix_lofted_entity()

    :returns: :class:`~ezdxf.math.Matrix44` object

RevolvedSurface
===============

.. class:: RevolvedSurface(Surface)

Introduced in DXF version R2007 (AC1021), dxftype is REVOLVEDSURFACE.

DXF Attributes for RevolvedSurface
----------------------------------

.. attribute:: RevolvedSurface.dxf.class_id

.. attribute:: RevolvedSurface.dxf.axis_point

.. attribute:: RevolvedSurface.dxf.axis_vector

.. attribute:: RevolvedSurface.dxf.revolve_angle

.. attribute:: RevolvedSurface.dxf.start_angle

.. attribute:: RevolvedSurface.dxf.draft_angle

.. attribute:: RevolvedSurface.dxf.start_draft_distance

.. attribute:: RevolvedSurface.dxf.end_draft_distance

.. attribute:: RevolvedSurface.dxf.twist_angle

.. attribute:: RevolvedSurface.dxf.solid

.. attribute:: RevolvedSurface.dxf.close_to_axis

RevolvedSurface Methods
-----------------------

.. method:: RevolvedSurface.set_transformation_matrix_revolved_entity(matrix)

    :param matrix: iterable of 16 numeric values.

.. method:: RevolvedSurface.get_transformation_matrix_revolved_entity()

    :returns: :class:`~ezdxf.math.Matrix44` object

SweptSurface
============

.. class:: SweptSurface(Surface)

Introduced in DXF version R2007 (AC1021), dxftype is SWEPTSURFACE.

DXF Attributes for SweptSurface
-------------------------------

.. attribute:: SweptSurface.dxf.swept_entity_id

.. attribute:: SweptSurface.dxf.path_entity_id

.. attribute:: SweptSurface.dxf.draft_angle

.. attribute:: SweptSurface.dxf.draft_start_distance

.. attribute:: SweptSurface.dxf.draft_end_distance

.. attribute:: SweptSurface.dxf.twist_angle

.. attribute:: SweptSurface.dxf.scale_factor

.. attribute:: SweptSurface.dxf.align_angle

.. attribute:: SweptSurface.dxf.solid

.. attribute:: SweptSurface.dxf.sweep_alignment

.. attribute:: SweptSurface.dxf.align_start

.. attribute:: SweptSurface.dxf.bank

.. attribute:: SweptSurface.dxf.base_point_set

.. attribute:: SweptSurface.dxf.sweep_entity_transform_computed

.. attribute:: SweptSurface.dxf.path_entity_transform_computed

.. attribute:: SweptSurface.dxf.reference_vector_for_controlling_twist

SweptSurface Methods
--------------------

.. method:: SweptSurface.set_transformation_matrix_sweep_entity(matrix)

    :param matrix: iterable of 16 numeric values.

.. method:: SweptSurface.get_transformation_matrix_sweep_entity()

    :returns: :class:`~ezdxf.math.Matrix44` object

.. method:: SweptSurface.set_transformation_matrix_path_entity(matrix)

    :param matrix: iterable of 16 numeric values.

.. method:: SweptSurface.get_transformation_matrix_path_entity()

    :returns: :class:`~ezdxf.math.Matrix44` object

.. method:: SweptSurface.set_sweep_entity_transformation_matrix(matrix)

    :param matrix: iterable of 16 numeric values.

.. method:: SweptSurface.get_sweep_entity_transformation_matrix()

    :returns: :class:`~ezdxf.math.Matrix44` object

.. method:: SweptSurface.set_path_entity_transformation_matrix(matrix)

    :param matrix: iterable of 16 numeric values.

.. method:: SweptSurface.get_path_entity_transformation_matrix()

    :returns: :class:`~ezdxf.math.Matrix44` object