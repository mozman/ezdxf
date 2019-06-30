============
Introduction
============

What is ezdxf
-------------

`ezdxf`  is a `Python`_ interface to the :term:`DXF` (drawing interchange file) format developed by `Autodesk`_,
it allows developers to read and modify existing DXF drawings or create new DXF drawings.

The main objective in the development of `ezdxf` was to hide complex DXF details from the programmer
but still support most capabilities of the :term:`DXF` format. Nevertheless, a basic understanding of the DXF
format is required, also to understand which goals are possible to accomplish with the DXF format.

Not all DXF features are supported yet, but additional features will be added in the future gradually.

`ezdxf` is also a replacement for my `dxfwrite`_ and my `dxfgrabber`_ packages but with different APIs, both packages
are in maintenance only mode, no new features will be added, but they stay available, getting bug fixes and will adapted
for new Python versions.

What ezdxf is NOT
-----------------

    - `ezdxf` is not a DXF converter: `ezdxf` can not convert between different DXF versions, if you are looking for an
      appropriate application, try the free `ODAFileConverter`_ from the `Open Design Alliance`_, which converts between
      different DXF version and also between the DXF and the DWG file format.
    - `ezdxf` is not a CAD file format converter: `ezdxf` can not convert DXF files to **ANY** other format, like SVG, PDF
      or DWG
    - `ezdxf` is not a DXF renderer, it does not create a visual representation of the DXF file content (see above).
    - `ezdxf` is not a CAD kernel, `ezdxf` does not provide any functionality for construction work, it is just an interface
      to the DXF file format. If you are looking for a CAD kernel with `Python`_ scripting support, look at `FreeCAD`_.


Supported Python Versions
-------------------------

`ezdxf` requires at least Python 3.5, for Python 2 support use `ezdxf` < v0.9.0, I run unit tests with the latest
stable CPython 3 version and the latest stable release of pypy3 during development.

`ezdxf` is written in pure Python and requires only `pyparser` as additional library beside the Python Standard Library.
`pytest` is required to run the provided unit and integration tests. Data to run the stress and audit test can not be
provided, because I don't have the rights for publishing this DXF files.

Supported Operating Systems
---------------------------

`ezdxf` is OS independent and runs on all platforms which provide an appropriate Python interpreter (>=3.6).

Supported DXF Versions
----------------------

.. include:: dxfversion.inc

`ezdxf` reads also older DXF versions but saves it as DXF R12.

Embedded DXF Information of 3rd Party Applications
--------------------------------------------------

The DXF format allows third-party applications to embed application-specific information.
`ezdxf` manages DXF data in a structure-preserving form, but for the price of large memory requirement.
Because of this, processing of DXF information of third-party applications is possible and will retained
on rewriting.

License
-------

`ezdxf` is licensed under the very liberal MIT-License_.

.. _Autodesk: http://usa.autodesk.com/

.. _Open Design Alliance: https://www.opendesign.com/

.. _ODAFileConverter: https://www.opendesign.com/guestfiles/oda_file_converter

.. _DXF: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-235B22E0-A567-4CF6-92D3-38A2306D73F3

.. _Python: http://www.python.org

.. _FreeCAD: https://www.freecadweb.org/

.. _MIT-License: http://opensource.org/licenses/mit-license.php

.. _dxfwrite: https://pypi.org/project/dxfwrite/

.. _dxfgrabber: https://pypi.org/project/dxfgrabber/
