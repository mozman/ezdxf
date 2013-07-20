
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
- no additional libraries required
- MIT-License
- supported DXF versions: R12, R2000, R2004, R2007, R2010 and R2013
- preserves third-party DXF content

a simple example::

    import ezdxf
    drawing = ezdxf.new(dxfversion='AC1024')
    modelspace = drawing.modelspace()
    modelspace.add_line((0, 0), (10, 0), dxfattribs={'color': 7})
    drawing.layers.create('TEXTLAYER', dxfattribs={'color': 2})
    modelspace.add_text('Test', dxfattribs={'insert': (0, 0.2), 'layer': 'TEXTLAYER'})
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
