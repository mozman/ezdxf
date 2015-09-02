============
Introduction
============

What is ezdxf
-------------

*ezdxf* is a Python package which allows developers to read existing DXF drawings or create new DXF drawings.

The main objective in the development of *ezdxf* was to hide complex DXF details from the programmer
but still support all the possibilities of the DXF format. Nevertheless, a basic understanding of the DXF
format is an advantage (but not necessary), also to understand what is possible with the DXF file format and what is
not.

*ezdxf* is still in its infancy, therefore not all DXF features supported yet, but additional features will be added in
the future gradually.

ezdxf is NOT
------------

- *ezdxf* is not a DXF converter: *ezdxf* can not convert between different DXF versions, if you are looking for an
  appropriate program, use *DWG TrueView* from `Autodesk`_, but the latest version can only convert to the DWG format,
  for converting between DXF versions you need at least AutoCAD LT.
- *ezdxf* is not a CAD file format converter: *ezdxf* can not convert DXF files to **ANY** other format, like SVG, PDF
  or DWG
- *ezdxf* is not a DXF renderer (see above)
- *ezdxf* is not a CAD kernel, *ezdxf* does not provide any functionality for construction work, it is just an interface
  to the DXF file format.

Supported Python Versions
-------------------------

*ezdxf* requires at least Python 2.7 and it's Python 3 compatible. I run unit tests with CPython 2.7, the latest stable
CPython 3 version and the latest stable release of pypy during development. *ezdxf* is written in pure Python
and requires only *pyparser* as additional library beside the Python Standard Library, hence it should run with
IronPython and Jython also.

Supported Operating Systems
---------------------------

*ezdxf* is OS independent and runs on all platforms which provide an appropriate Python interpreter (>=2.7).

Supported DXF Versions
----------------------

.. include:: dxfversion.inc

Embedded DXF Information of 3rd Party Applications
--------------------------------------------------

The DXF format allows third-party applications to embed application-specific information.
*ezdxf* manages DXF data in a structure-preserving form, but for the price of large memory requirement.
Because of this, processing of DXF information of third-party applications is possible and will retained
on rewriting.

License
-------

*ezdxf* is licensed under the very liberal MIT-License_.

.. _Autodesk: http://usa.autodesk.com/

.. _MIT-License: http://opensource.org/licenses/mit-license.php