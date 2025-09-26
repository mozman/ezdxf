============
Introduction
============

What is ezdxf
-------------

`Ezdxf`  is a `Python`_ interface to the :term:`DXF` (drawing interchange file)
format developed by `Autodesk`_, `ezdxf` allows developers to read and modify
existing DXF documents or create new DXF documents.

The main objective in the development of `ezdxf` was to hide complex DXF details
from the programmer but still support most capabilities of the :term:`DXF`
format. Nevertheless, a basic understanding of the DXF format is required, also
to understand which tasks and goals are possible to accomplish by using the
DXF format.

Not all DXF features are supported yet, but additional features will be added in
the future gradually.

`Ezdxf` is also a replacement for the outdated `dxfwrite`_ and `dxfgrabber`_
packages but with different APIs, for more information see also: :ref:`faq001`

What ezdxf can't do
-------------------

- `ezdxf` is not a DXF converter: `ezdxf` can not convert between different
  DXF versions, if you are looking for an appropriate application, try the
  free `ODAFileConverter`_ from the `Open Design Alliance`_, which converts
  between different DXF version and also between the DXF and the DWG file format.
- `ezdxf` is not a CAD file format converter: `ezdxf` can not convert DXF files
  to other CAD formats such as DWG
- `ezdxf` is not a CAD kernel and does not provide high level functionality for
  construction work, it is just an interface to the DXF file format. If you are
  looking for a CAD kernel with `Python`_ scripting support, look at `FreeCAD`_.


Supported Python Versions
-------------------------

`Ezdxf` requires at least Python 3.10 and will be tested with the
latest stable CPython version and the latest stable release of pypy3 during development.

`Ezdxf` is written in pure Python with optional Cython implementations of some
low level math classes and requires `pyparsing`, `numpy`, `fontTools` and
`typing_extensions` as additional library beside the Python Standard Library.
`Pytest` is required to run the unit and integration tests. Data to run the
stress and audit test can not be provided, because I don't have the rights for
publishing these DXF files.

Supported Operating Systems
---------------------------

`Ezdxf` is OS independent and runs on all platforms which provide an appropriate
Python interpreter (>=3.10).

Supported DXF Versions
----------------------

.. include:: dxfversion.inc

`Ezdxf` also reads older DXF versions but saves it as DXF R12.

Embedded DXF Information of 3rd Party Applications
--------------------------------------------------

The DXF format allows third-party applications to embed application-specific
information. `Ezdxf` manages DXF data in a structure-preserving form, but for
the price of large memory requirement. Because of this, processing of DXF
information of third-party applications is possible and will retained on
rewriting.

License
-------

`Ezdxf` is licensed under the very liberal MIT-License_.

.. _Autodesk: http://usa.autodesk.com/

.. _Open Design Alliance: https://www.opendesign.com/

.. _ODAFileConverter: https://www.opendesign.com/guestfiles/oda_file_converter

.. _DXF: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-235B22E0-A567-4CF6-92D3-38A2306D73F3

.. _Python: http://www.python.org

.. _FreeCAD: https://www.freecadweb.org/

.. _MIT-License: http://opensource.org/licenses/mit-license.php

.. _dxfwrite: https://pypi.org/project/dxfwrite/

.. _dxfgrabber: https://pypi.org/project/dxfgrabber/
