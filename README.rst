
ezdxf
=====

Abstract
--------

A Python package to create and modify DXF drawings, independent from the DXF
version. You can open/save every DXF file without loosing any content (except comments),
Unknown tags in the DXF file will be ignored but preserved for saving. With this behavior
it is possible to open also DXF drawings that contains data from 3rd party applications.

Quick-Info
----------

- *ezdxf* is a Python package to read and write DXF drawings
- intended audience: Developer
- requires Python 2.7 or later, runs on CPython and pypy, maybe on IronPython and Jython
- OS independent
- additional required packages: `pyparsing <https://pypi.python.org/pypi/pyparsing/2.0.1>`_
- MIT-License
- supported DXF versions read/new: R12, R2000, R2004, R2007, R2010 and R2013
- experimental support for DXF versions R13/R14 (AC1012/AC1014), will be saved as R2000 (AC1015)
- reads also older versions but saves it as R12
- preserves third-party DXF content

a simple example::

    import ezdxf
    drawing = ezdxf.new(dxfversion='AC1024')  # or use the AutoCAD release name ezdxf.new(dxfversion='R2010')
    modelspace = drawing.modelspace()
    modelspace.add_line((0, 0), (10, 0), dxfattribs={'color': 7})
    drawing.layers.new('TEXTLAYER', dxfattribs={'color': 2})
    # use set_pos() for proper TEXT alignment - the relations between halign, valign, insert and align_point are tricky.
    modelspace.add_text('Test', dxfattribs={'layer': 'TEXTLAYER'}).set_pos((0, 0.2), align='CENTER')
    drawing.saveas('test.dxf')

Installation
============

Install with pip::

    pip install ezdxf

or from source::

    python setup.py install

Documentation
=============

http://pythonhosted.org/ezdxf

http://ezdxf.readthedocs.org/

The source code of ezdxf can be found on bitbucket.org at:

http://bitbucket.org/mozman/ezdxf

Feedback
========

Issue Tracker at:

https://bitbucket.org/mozman/ezdxf/issues

Feedback, Q&A, Discussions at Google Groups:

https://groups.google.com/d/forum/python-ezdxf

Mailing List:

python-ezdxf@googlegroups.com

Feedback is greatly appreciated.

Manfred

mozman@gmx.at
