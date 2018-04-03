UnderlayDefinition
==================

.. class:: UnderlayDefinition(DXFObject)

Introduced in DXF version R13 (AC1012), dxftype is PDFDEFINITION, DWFDEFINITION and DGNDEFINITION.

:class:`UnderlayDefinition` defines an underlay, which can be placed by the :class:`Underlay` entity. Create
:class:`UnderlayDefinition` by the :class:`Drawing` factory function :meth:`~Drawing.add_underlay_def`.


DXF Attributes for UnderlayDefinition
-------------------------------------

.. attribute:: UnderlayDefinition.dxf.filename

    Relative (to the DXF file) or absolute path to the image file as string

.. attribute:: UnderlayDefinition.dxf.name

    defines what to display

    - pdf: page number
    - dgn: 'default'
    - dwf: ???



