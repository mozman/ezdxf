Const
=====

.. module:: ezdxf.lldxf.const

The module :mod:`ezdxf.lldxf.const`, is also accessible from the ``ezdxf``
namespace::

    from ezdxf.lldxf.const import DXF12
    import ezdxf

    print(DXF12)
    print(ezdxf.const.DXF12)

DXF Version Strings
-------------------

======= =========== =======
Name    Version     Alias
======= =========== =======
DXF9    "AC1004"    "R9"
DXF10   "AC1006"    "R10"
DXF12   "AC1009"    "R12"
DXF13   "AC1012"    "R13"
DXF14   "AC1014"    "R14"
DXF2000 "AC1015"    "R2000"
DXF2004 "AC1018"    "R2004"
DXF2007 "AC1021"    "R2007"
DXF2010 "AC1024"    "R2010"
DXF2013 "AC1027"    "R2013"
DXF2018 "AC1032"    "R2018"
======= =========== =======

Exceptions
----------

.. autoclass:: DXFError

.. autoclass:: DXFStructureError(DXFError)

.. autoclass:: DXFVersionError(DXFError)

.. autoclass:: DXFValueError(DXFError)

.. autoclass:: DXFInvalidLineType(DXFValueError)

.. autoclass:: DXFBlockInUseError(DXFValueError)

.. autoclass:: DXFKeyError(DXFError)

.. autoclass:: DXFUndefinedBlockError(DXFKeyError)

.. autoclass:: DXFAttributeError(DXFError)

.. autoclass:: DXFIndexError(DXFError)

.. autoclass:: DXFTypeError(DXFError)

.. autoclass:: DXFTableEntryError(DXFValueError)
