UnderlayDefinition
==================

.. module:: ezdxf.entities
    :noindex:

:class:`UnderlayDefinition` (`DXF Reference`_) defines an underlay file, which can be placed by the :class:`Underlay` entity.

======================== ==============================================================
Subclass of              :class:`ezdxf.entities.DXFObject`
DXF type                 internal base class
Factory function (1)     :meth:`ezdxf.drawing.Drawing.add_underlay_def`
Factory function (2)     :meth:`ezdxf.sections.objects.ObjectsSection.add_underlay_def`
======================== ==============================================================

.. class:: UnderlayDefinition

   Base class of :class:`PdfDefinition`, :class:`DwfDefinition` and :class:`DgnDefinition`

    .. attribute:: dxf.filename

        Relative (to the DXF file) or absolute path to the underlay file as string.

    .. attribute:: dxf.name

        Defines which part of the underlay file to display.

        ========= ============================
        ``'pdf'`` PDF page number
        ``'dgn'`` always ``'default'``
        ``'dwf'`` ?
        ========= ============================

.. warning::

    Do not instantiate object classes by yourself - always use the provided factory functions!

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A4FF15D3-F745-4E1F-94D4-1DC3DF297B0F

PdfDefinition
-------------

======================== ==============================================================
Subclass of              :class:`ezdxf.entities.UnderlayDefinition`
DXF type                 ``'PDFDEFINITION'``
Factory function (1)     :meth:`ezdxf.drawing.Drawing.add_underlay_def`
Factory function (2)     :meth:`ezdxf.sections.objects.ObjectsSection.add_underlay_def`
======================== ==============================================================

.. class:: PdfDefinition

    PDF underlay file.

DwfDefinition
-------------

======================== ==============================================================
Subclass of              :class:`ezdxf.entities.UnderlayDefinition`
DXF type                 ``'DWFDEFINITION'``
Factory function (1)     :meth:`ezdxf.drawing.Drawing.add_underlay_def`
Factory function (2)     :meth:`ezdxf.sections.objects.ObjectsSection.add_underlay_def`
======================== ==============================================================

.. class:: DwfDefinition

    DWF underlay file.

DgnDefinition
-------------

======================== ==============================================================
Subclass of              :class:`ezdxf.entities.UnderlayDefinition`
DXF type                 ``'DGNDEFINITION'``
Factory function (1)     :meth:`ezdxf.drawing.Drawing.add_underlay_def`
Factory function (2)     :meth:`ezdxf.sections.objects.ObjectsSection.add_underlay_def`
======================== ==============================================================

.. class:: DgnDefinition

    DGN underlay file.

