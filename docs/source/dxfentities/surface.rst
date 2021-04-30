Surface
=======

.. module:: ezdxf.entities
    :noindex:

SURFACE (`DXF Reference`_) created by an ACIS based geometry kernel provided by
the `Spatial Corp.`_

.. seealso::

    `Ezdxf` will never create or interpret ACIS data, for more information see
    the FAQ: :ref:`faq003`


======================== ==========================================
Subclass of              :class:`ezdxf.entities.Body`
DXF type                 ``'SURFACE'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_surface`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Surface

    Same attributes and methods as parent class :class:`Body`.

    .. attribute:: dxf.u_count

        Number of U isolines.

    .. attribute:: dxf.v_count

        Number of V2 isolines.

.. _Spatial Corp.: http://www.spatial.com/products/3d-acis-modeling

ExtrudedSurface
---------------

(`DXF Reference`_)

======================== ==========================================
Subclass of              :class:`ezdxf.entities.Surface`
DXF type                 ``'EXTRUDEDSURFACE'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_extruded_surface`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2007 (``'AC1021'``)
======================== ==========================================

.. class:: ExtrudedSurface

    Same attributes and methods as parent class :class:`Surface`.

    .. attribute:: dxf.class_id

    .. attribute:: dxf.sweep_vector

    .. attribute:: dxf.draft_angle

    .. attribute:: dxf.draft_start_distance

    .. attribute:: dxf.draft_end_distance

    .. attribute:: dxf.twist_angle

    .. attribute:: dxf.scale_factor

    .. attribute:: dxf.align_angle

    .. attribute:: dxf.solid

    .. attribute:: dxf.sweep_alignment_flags

        === ===============================
        0   No alignment
        1   Align sweep entity to path
        2   Translate sweep entity to path
        3   Translate path to sweep entity
        === ===============================

    .. attribute:: dxf.align_start

    .. attribute:: dxf.bank

    .. attribute:: dxf.base_point_set

    .. attribute:: dxf.sweep_entity_transform_computed

    .. attribute:: dxf.path_entity_transform_computed

    .. attribute:: dxf.reference_vector_for_controlling_twist

    .. attribute:: transformation_matrix_extruded_entity

        type: :class:`~ezdxf.math.Matrix44`

    .. attribute:: sweep_entity_transformation_matrix

        type: :class:`~ezdxf.math.Matrix44`

    .. attribute:: path_entity_transformation_matrix

        type: :class:`~ezdxf.math.Matrix44`

LoftedSurface
-------------

(`DXF Reference`_)

======================== ==========================================
Subclass of              :class:`ezdxf.entities.Surface`
DXF type                 ``'LOFTEDSURFACE'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_lofted_surface`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2007 (``'AC1021'``)
======================== ==========================================

.. class:: LoftedSurface

    Same attributes and methods as parent class :class:`Surface`.

    .. attribute:: dxf.plane_normal_lofting_type

    .. attribute:: dxf.start_draft_angle

    .. attribute:: dxf.end_draft_angle

    .. attribute:: dxf.start_draft_magnitude

    .. attribute:: dxf.end_draft_magnitude

    .. attribute:: dxf.arc_length_parameterization

    .. attribute:: dxf.no_twist

    .. attribute:: dxf.align_direction

    .. attribute:: dxf.simple_surfaces

    .. attribute:: dxf.closed_surfaces

    .. attribute:: dxf.solid

    .. attribute:: dxf.ruled_surface

    .. attribute:: dxf.virtual_guide

    .. attribute:: set_transformation_matrix_lofted_entity

        type: :class:`~ezdxf.math.Matrix44`

RevolvedSurface
---------------

(`DXF Reference`_)

======================== ==========================================
Subclass of              :class:`ezdxf.entities.Surface`
DXF type                 ``'REVOLVEDSURFACE'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_revolved_surface`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2007 (``'AC1021'``)
======================== ==========================================

.. class:: RevolvedSurface

    Same attributes and methods as parent class :class:`Surface`.

    .. attribute:: dxf.class_id

    .. attribute:: dxf.axis_point

    .. attribute:: dxf.axis_vector

    .. attribute:: dxf.revolve_angle

    .. attribute:: RevolvedSurface.dxf.start_angle

    .. attribute:: dxf.draft_angle

    .. attribute:: dxf.start_draft_distance

    .. attribute:: dxf.end_draft_distance

    .. attribute:: dxf.twist_angle

    .. attribute:: dxf.solid

    .. attribute:: dxf.close_to_axis

    .. attribute:: transformation_matrix_revolved_entity

        type: :class:`~ezdxf.math.Matrix44`

SweptSurface
------------

(`DXF Reference`_)

======================== ==========================================
Subclass of              :class:`ezdxf.entities.Surface`
DXF type                 ``'SWEPTSURFACE'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_swept_surface`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2007 (``'AC1021'``)
======================== ==========================================

.. class:: SweptSurface

    Same attributes and methods as parent class :class:`Surface`.

    .. attribute:: dxf.swept_entity_id

    .. attribute:: dxf.path_entity_id

    .. attribute:: dxf.draft_angle

    .. attribute:: draft_start_distance

    .. attribute:: dxf.draft_end_distance

    .. attribute:: dxf.twist_angle

    .. attribute:: dxf.scale_factor

    .. attribute:: dxf.align_angle

    .. attribute:: dxf.solid

    .. attribute:: dxf.sweep_alignment

    .. attribute:: dxf.align_start

    .. attribute:: dxf.bank

    .. attribute:: dxf.base_point_set

    .. attribute:: dxf.sweep_entity_transform_computed

    .. attribute:: dxf.path_entity_transform_computed

    .. attribute:: dxf.reference_vector_for_controlling_twist

    .. attribute:: transformation_matrix_sweep_entity

        type: :class:`~ezdxf.math.Matrix44`

    .. method:: transformation_matrix_path_entity

        type: :class:`~ezdxf.math.Matrix44`

    .. method:: sweep_entity_transformation_matrix

        type: :class:`~ezdxf.math.Matrix44`

    .. method:: path_entity_transformation_matrix

        type: :class:`~ezdxf.math.Matrix44`

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-BB62483A-89C3-47C4-80E5-EA3F08979863