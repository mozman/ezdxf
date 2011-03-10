
ezdxf
=====

Abstract
--------

A Python package to create and modify DXF drawings, independent from the DXF
version. Important: ezdxf is not a conversion tool, so if you open a DXF R12
drawing, you can not save the drawing as R2000 DXF file, but you can open or
create new DXF drawings for every supported DXF version.
You can open/save every DXF file without loosing any content, but not every
content is supported by this package. Unknown tags in the DXF files were simple
ignored but preserved for saving. With this behavior it should be possible to
open also newer DXF versions without problems.

Supported DXF Version
---------------------

======= ========================
Version introduced with AutoCAD
======= ========================
R12     AutoCAD V12
R2000   AutoCAD V2000
R2004   AutoCAD V2004
R2007   AutoCAD V2007
R2010   AutoCAD V2010
======= ========================

a simple example::

    import ezdxf
    drawing = ezdxf.new('test.dxf', version='R2010')
    dxf = drawing.get_dxfengine()
    drawing.add(dxf.line((0, 0), (10, 0), color=7))
    drawing.add_layer('TEXTLAYER', color=2)
    drawing.add(dxf.text('Test', insert=(0, 0.2), layer='TEXTLAYER')
    drawing.save()

supported DXF entities
----------------------

 * ARC
 * ATTDEF
 * ATTRIB
 * BLOCK
 * CIRCLE
 * 3DFACE
 * INSERT
 * LINE
 * POINT
 * POLYLINE (special Polyface and Polymesh objects are available)
 * SHAPE (not tested)
 * SOLID
 * TRACE
 * TEXT
 * VERTEX (only for internal use, see Polyline, Polyface and Polymesh objects)
 * MTEXT
 * ELLIPSE
 * SPLINE
 * LWPOLYLINE

read/write AutoCAD ctb-files
----------------------------

The module ``acadctb`` provides the ability to read and write AutoCAD ctb-files.
With ctb-files you can assign a new color or lineweight to a dxf-color-index for
plotting or printing, but this has to be supported by the used application.

a simple example::

    from ezdxf import acadctb
    ctb = acadctb.load('test.ctb')
    style1 = ctb.get_style(1) # dxf color index (1 .. 255)
    style1.set_color(23, 177, 68) # set rgb values (0..255)
    style1.set_lineweight(0.7)
    ctb.save('new.ctb')

Installation
============

with easy_install::

    easy_install ezdxf

with pip::

    pip install dxfwrite

or from source::

    python setup.py install

Documentation
=============

http://packages.python.org/ezdxf/

Good Luck! Feedback is greatly appreciated.

Manfred

mozman@gmx.at

ezdxf can be found on bitbucket.org at:

http://bitbucket.org/mozman/ezdxf
