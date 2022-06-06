.. ezdxf documentation master file, created by
   sphinx-quickstart on Tue Mar 15 06:49:46 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: gfx/ezdxf-logo-light-bg.svg
   :align: center
   :width: 400px

Welcome! This is the documentation for ezdxf release |release|, last updated |today|.

Quick-Info
==========

- *ezdxf* is a Python package to create new DXF files and read/modify/write existing DXF files
- the intended audience are programmers
- requires at least Python 3.7
- OS independent
- additional required packages: `pyparsing <https://pypi.python.org/pypi/pyparsing/>`_
- optional Cython implementation of some low level math classes
- MIT-License
- read/write/new support for DXF versions: R12, R2000, R2004, R2007, R2010, R2013 and R2018
- additional read support for DXF versions R13/R14 (upgraded to R2000)
- additional read support for older DXF versions than R12 (upgraded to R12)
- read/write support for ASCII DXF and Binary DXF
- preserves third-party DXF content

Included Extensions
-------------------

- :mod:`~ezdxf.addons.drawing` add-on to visualise and convert DXF files to
  images which can be saved to various formats such as png, pdf and svg
- :mod:`~ezdxf.addons.geo` add-on to support the `__geo_interface__ <https://gist.github.com/sgillies/2217756>`_
- :mod:`~ezdxf.addons.r12writer` add-on to write basic DXF entities direct and
  fast into a DXF R12 file or stream
- :mod:`~ezdxf.addons.iterdxf` add-on to iterate over entities of the modelspace
  of really big (> 5GB) DXF files which do not fit into memory
- :mod:`~ezdxf.addons.importer` add-on to import entities, blocks and table
  entries from another DXF document
- :mod:`~ezdxf.addons.dxf2code` add-on to generate Python code for DXF structures
  loaded from DXF documents as starting point for parametric DXF entity creation
- :mod:`~ezdxf.addons.acadctb` add-on to read/write :ref:`plot_style_files`
- :class:`~ezdxf.addons.MTextExplode` add-on for exploding MTEXT entities into
  single line TEXT entities
- :class:`~ezdxf.addons.meshex` add-on for mesh exchange with other tools in
  various file formats
- :class:`~ezdxf.addons.openscad` add-on uses the `OpenSCAD <https://openscad.org/>`_
  application to apply boolean operations to meshes
- :mod:`~ezdxf.addons.pycsg` add-on for Constructive Solid Geometry (CSG)
  modeling technique

Website
-------

https://ezdxf.mozman.at/

Documentation
-------------

Documentation of development version at https://ezdxf.mozman.at/docs

Documentation of latest release at http://ezdxf.readthedocs.io/

Source Code & Feedback
----------------------

Source Code: http://github.com/mozman/ezdxf.git

Issue Tracker: http://github.com/mozman/ezdxf/issues

Forum: https://github.com/mozman/ezdxf/discussions

Questions and Answers
---------------------

Please post questions at the `forum <https://github.com/mozman/ezdxf/discussions>`_ or
`stack overflow <https://stackoverflow.com/>`_ to make answers available to other users as well.


Contents
========

.. toctree::
   :maxdepth: 2

   introduction
   setup
   usage_for_beginners
   concepts/index
   tutorials/index
   howto/index
   faq
   reference
   launcher
   render/index
   addons/index
   dxfinternals/index
   develop/index
   glossary

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`

