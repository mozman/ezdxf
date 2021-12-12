Glossary
========

.. glossary::

    ACI
        :ref:`ACI`

    ACIS
        The 3D ACIS Modeler (`ACIS`_) is a geometric modeling kernel developed
        by `Spatial Corp.`_ ® (formerly Spatial Technology), part of Dassault
        Systems.

    bulge
        The :ref:`bulge value` is used to create arc shaped line segments in
        :class:`~ezdxf.entities.Polyline` and :class:`~ezdxf.entities.LWPolyline`
        entities.

    CAD
        Computer-Assisted Drafting or Computer-Aided Design

    CTB
        Color dependent plot style table (:class:`~ezdxf.acadctb.ColorDependentPlotStyles`)

    DWG
        Proprietary file format of `AutoCAD`_ ®. Documentation for this format
        is available from the Open Design Alliance (`ODA`_) at their `Downloads`_
        section. This documentation is created by reverse engineering therefore
        not perfect nor complete.

    DXF
        Drawing eXchange Format is a file format used by `AutoCAD`_ ® to
        interchange data with other :term:`CAD` applications. `DXF`_ is a
        trademark of `Autodesk`_ ®. See also :ref:`what is dxf`

    STB
        Named plot style table (:class:`~ezdxf.acadctb.NamedPlotStyles`)

    true color
        RGB color representation, a combination red, green and blue values to
        define a color.

    raw color
        Raw color value as stored in DWG files, this integer value can
        represent :term:`ACI` values as well as and :term:`true color` values

    reliable CAD application
        CAD applications which create valid DXF documents in the meaning and
        interpretation of `Autodesk`_. See also :ref:`what is dxf`


.. (R) = Atl+0174

.. _Autodesk: https://www.autodesk.com/

.. _AutoCAD: https://www.autodesk.com/products/autocad/overview

.. _DXF: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-235B22E0-A567-4CF6-92D3-38A2306D73F3

.. _Spatial Corp.: http://www.spatial.com/products/3d-acis-modeling

.. _ACIS: https://en.wikipedia.org/wiki/ACIS

.. _ODA: https://www.opendesign.com/

.. _downloads: https://www.opendesign.com/guestfiles