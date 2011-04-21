
ezdxf
=====

Abstract
--------

A Python package to create and modify DXF drawings, independent from the DXF
version. Important: ezdxf is not a converting tool, so if you open a DXF R12
drawing, you can not save the drawing as DXF R2000 file, but you can open or
create new DXF drawings for every supported DXF version. If you need a DXF
converter search for the free program *DWG TrueView* from Autodesk.
You can open/save every DXF file without loosing any content, but not every
content is supported by this package. Unknown tags in the DXF files were simple
ignored but preserved for saving. With this behavior it should be possible to
open also newer DXF versions without problems.

Supported DXF Version
---------------------

======= ========================
Version introduced with AutoCAD
======= ========================
AC1009  AutoCAD V12
AC1015  AutoCAD V2000
AC1018  AutoCAD V2004
AC1020  AutoCAD V2007
AC1024  AutoCAD V2010
======= ========================

a simple example::

    import ezdxf
    drawing = ezdxf.new('test.dxf', version='R2010')
    dxf = drawing.get_dxfengine()
    drawing.add(dxf.line((0, 0), (10, 0), color=7))
    drawing.add_layer('TEXTLAYER', color=2)
    drawing.add(dxf.text('Test', insert=(0, 0.2), layer='TEXTLAYER')
    drawing.save()

Installation
============

from source::

    python setup.py install

Documentation
=============

http://packages.python.org/ezdxf/

Feedback is greatly appreciated.

Manfred

mozman@gmx.at

ezdxf can be found on bitbucket.org at:

http://bitbucket.org/mozman/ezdxf
