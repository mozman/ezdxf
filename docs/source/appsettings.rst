
.. _ezdxf_appsettings:

Application Settings
====================

.. versionadded:: 0.18

.. module:: ezdxf.appsettings

This is a high level module for working with CAD application settings and
behaviors.
All these settings have no influence on the behavior of `ezdxf`, since `ezdxf`
only takes care of the content of the DXF file and not of the way it is
presented to the user.

.. important::

    You have to understand that this settings work at application level,
    `ezdxf` cannot force an application to do something at a specific way!
    The functions of this module are tested with Autodesk TrueView and BricsCAD,
    other applications may show different results or ignore the settings at all.

The module :mod:`ezdxf.gfxattribs` provides the class :meth:`~ezdxf.gfxattribs.GfxAttribs`,
which can load the current graphical entity settings from the HEADER section
for creating new entities by `ezdxf`: :meth:`~ezdxf.gfxattribs.GfxAttribs.load_from_header`


Set Current Properties
----------------------

The current properties are used by the CAD application to create new entities,
these settings do not affect how `ezdxf` creates new entities.

.. autofunction:: set_current_layer

.. autofunction:: set_current_color

.. autofunction:: set_current_linetype

.. autofunction:: set_current_lineweight

.. autofunction:: set_current_linetype_scale

.. autofunction:: set_current_textstyle

.. autofunction:: set_current_dimstyle

.. autofunction:: restore_wcs

work in progress
