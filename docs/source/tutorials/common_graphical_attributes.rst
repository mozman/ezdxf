.. _tut_common_graphical_attributes:

Tutorial for Common Graphical Attributes
========================================

The graphical attributes :attr:`color`, :attr:`linetype`, :attr:`lineweight`,
:attr:`true_color`, :attr:`transparency`, :attr:`ltscale` and :attr:`invisible`
are available for all graphical DXF entities and are located in the DXF
namespace attribute :attr:`dxf` of the DXF entities.
All these attributes are optional and all except for :attr:`true_color` and
:attr:`transparency` have a default value.

Not all of these attributes are supported by all DXF versions. This table
shows the minimum required DXF version for each attribute:

======= =======================================================
R12     :attr:`color`, :attr:`linetype`
R2000   :attr:`lineweight`, :attr:`ltscale`, :attr:`invisible`
R2004   :attr:`true_color`, :attr:`transparency`
======= =======================================================

Color
-----

True Color
----------

Transparency
------------

Linetype
--------

Lineweight
----------

Linetype Scale
--------------

Invisible
---------
