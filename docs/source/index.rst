.. ezdxf documentation master file, created by
   sphinx-quickstart on Tue Mar 15 06:49:46 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ezdxf |version| documentation
=============================

Welcome! This is the documentation for ezdxf |version|, last updated |today|.

Description
-----------

*ezdxf* is a python-package to *read and write DXF drawings*,
independent from the DXF version. Important: ezdxf is not a converting tool,
so if you open a DXF R12 drawing, you can not save the drawing as DXF R2000
file, but you can open or create new DXF drawings for every supported DXF
version. (If you need a DXF converter search for the free program *DWG TrueView*
from `Autodesk`_.)

You can open/save every DXF file without loosing any content, but not every
content is supported by this package. Unknown tags in the DXF files will be
ignored but preserved for saving. With this behavior it should be possible to
open also DXF drawings that contains data from 3rd party applications.

Supported DXF Versions
----------------------

======= ========================
Version introduced with AutoCAD
======= ========================
AC1009  AutoCAD V12
AC1015  AutoCAD V2000
AC1018  AutoCAD V2004
AC1021  AutoCAD V2007
AC1024  AutoCAD V2010
AC1027  AutoCAD V2013 (soon)
======= ========================

Contents:
---------

.. toctree::
   :maxdepth: 2

   introduction
   tutorials
   reference
   howto

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Autodesk: http://usa.autodesk.com/
