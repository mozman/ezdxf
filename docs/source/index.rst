.. ezdxf documentation master file, created by
   sphinx-quickstart on Tue Mar 15 06:49:46 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=====
ezdxf
=====

Welcome! This is the documentation for ezdxf |version|, last updated |today|.


Quick-Info
----------

- *ezdxf* is a Python package to read and write DXF drawings (interface to the DXF file format)
- intended audience: Developer
- requires Python 2.7 or later, runs on CPython and pypy, maybe on IronPython and Jython
- OS independent
- additional packages required: `pyparsing <https://pypi.python.org/pypi/pyparsing/2.0.1>`_
- MIT-License
- supported DXF versions read/new: R12, R2000, R2004, R2007, R2010 and R2013
- support for DXF versions R13/R14 (AC1012/AC1014), will be upgraded to R2000 (AC1015)
- support for older versions than R12, will be upgraded to R12 (AC1009)
- preserves third-party DXF content
- additional :ref:`r12writer`, just the ENTITIES section with support for  LINE, CIRCLE, ARC,
  TEXT, POINT, SOLID, 3DFACE and POLYLINE.

Contents
--------

.. toctree::
   :maxdepth: 2

   introduction
   tutorials
   reference
   howto
   dxfinternals

.. include:: ../../NEWS.rst
   :end-before: Version 0.6.5

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`


