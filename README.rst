
ezdxf
=====

.. image:: https://readthedocs.org/projects/pip/badge/
   :target: https://ezdxf.readthedocs.io
   :alt: Read The Docs

Abstract
--------

A Python package to create and modify DXF drawings, independent from the DXF
version. You can open/save every DXF file without loosing any content (except comments),
Unknown tags in the DXF file will be ignored but preserved for saving. With this behavior
it is possible to open also DXF drawings that contains data from 3rd party applications.

Quick-Info
----------

- ezdxf is a Python package to create new DXF files and read/modify/write existing DXF files
- the intended audience are developers
- requires Python 2.7 or later, runs on CPython and pypy, maybe on IronPython and Jython
- OS independent
- additional required packages: `pyparsing <https://pypi.python.org/pypi/pyparsing/2.0.1>`_
- MIT-License
- read/write/new support for DXF versions: R12, R2000, R2004, R2007, R2010, R2013 and R2018
- additional read support for DXF versions R13/R14 (upgraded to R2000)
- additional read support for older DXF versions than R12 (upgraded to R12)
- preserves third-party DXF content
- additional fast DXF R12 writer, that creates just an ENTITIES section with support for the basic DXF entities

a simple example::

    import ezdxf

    drawing = ezdxf.new(dxfversion='AC1024')  # or use the AutoCAD release name ezdxf.new(dxfversion='R2010')
    modelspace = drawing.modelspace()
    modelspace.add_line((0, 0), (10, 0), dxfattribs={'color': 7})
    drawing.layers.new('TEXTLAYER', dxfattribs={'color': 2})
    # use set_pos() for proper TEXT alignment - the relations between halign, valign, insert and align_point are tricky.
    modelspace.add_text('Test', dxfattribs={'layer': 'TEXTLAYER'}).set_pos((0, 0.2), align='CENTER')
    drawing.saveas('test.dxf')

example for the *r12writer*, writes a simple DXF R12 file without in-memory structures::

    from random import random
    from ezdxf.r12writer import r12writer

    MAX_X_COORD = 1000.0
    MAX_Y_COORD = 1000.0
    CIRCLE_COUNT = 100000

    with r12writer("many_circles.dxf") as dxf:
        for i in range(CIRCLE_COUNT):
            dxf.add_circle((MAX_X_COORD*random(), MAX_Y_COORD*random()), radius=2)

The r12writer supports only the ENTITIES section of a DXF R12 drawing, no HEADER, TABLES or BLOCKS section is
present, except FIXED-TABLES are written, than some additional predefined text styles and line types are available.

Installation
============

Install with pip::

    pip install ezdxf

or from source::

    python setup.py install

Website
=======

https://sites.google.com/view/ezdxf

Documentation
=============

http://ezdxf.readthedocs.io/

The source code of ezdxf can be found at GitHub.com:

http://github.com/mozman/ezdxf.git

Feedback
========

Issue Tracker at:

http://github.com/mozman/ezdxf/issues

Questions and Feedback at Google Groups:

https://groups.google.com/d/forum/python-ezdxf

Mailing List:

python-ezdxf@googlegroups.com

Feedback is greatly appreciated.

Manfred

mozman@gmx.at
