DimStyle
========

.. class:: DimStyle

Defines a dimension style.

.. image:: ../dxfinternals/gfx/dimvars1.svg
    :align: center
    :width: 800px

.. image:: ../dxfinternals/gfx/dimvars2.svg
    :align: center
    :width: 800px

DXF Attributes for DimStyle
---------------------------

.. attribute:: DimStyle.dxf.handle

Handle of table entry.

.. attribute:: DimStyle.dxf.owner

Handle to dimstyle table, requires DXF R13 or later

.. attribute:: DimStyle.dxf.name

Text style name.

.. attribute:: DimStyle.dxf.flags

Standard flag values (bit-coded values):

- 16 = If set, table entry is externally dependent on an xref
- 32 = If both this bit and bit 16 are set, the externally dependent xref has been successfully resolved
- 64 = If set, the table entry was referenced by at least one entity in the drawing the last time the drawing
  was edited. (This flag is for the benefit of AutoCAD commands. It can be ignored by most programs that read
  DXF files and need not be set by programs that write DXF files)

.. attribute:: DimStyle.dxf.dimpost

Prefix/suffix for primary units dimension values.

.. attribute:: DimStyle.dxf.dimapost

Prefix/suffix for alternate units dimensions.

.. attribute:: DimStyle.dxf.dimblk

Block type to use for both arrowheads as name string.

.. attribute:: DimStyle.dxf.dimblk1

Block type to use for first arrowhead as name string.

.. attribute:: DimStyle.dxf.dimblk2

Block type to use for second arrowhead as name string.

.. attribute:: DimStyle.dxf.dimscale

Global dimension feature scale factor. (default=1.)

.. attribute:: DimStyle.dxf.dimasz

Dimension line and arrowhead size. (default=0.28)

.. attribute:: DimStyle.dxf.dimexo

Distance from origin points to extension lines. (default imperial=0.0625, default metric=0.625)

.. attribute:: DimStyle.dxf.dimdli

Incremental spacing between baseline dimensions. (default imperial=0.38, default metric=3.75)

.. attribute:: DimStyle.dxf.dimexe

Extension line distance beyond dimension line. (default imperial=0.28, default metric=2.25)

.. attribute:: DimStyle.dxf.dimrnd

Rounding value for dimensions. (default=0)

.. attribute:: DimStyle.dxf.dimdle

Dimension line extension beyond extension lines. (default=0)

.. attribute:: DimStyle.dxf.dimtp

Upper tolerance value for tolerance dimensions. (default=0)

.. attribute:: DimStyle.dxf.dimtm

Lower tolerance value for tolerance dimensions. (default=0)

.. attribute:: DimStyle.dxf.dimtxt

Size of dimension text. (default imperial=0.28, default metric=2.5)

.. attribute:: DimStyle.dxf.dimcen

Controls placement of center marks or centerlines. (default imperial=0.09, default metric=2.5)

.. attribute:: DimStyle.dxf.dimtsz

Controls size of dimension line tick marks drawn instead of arrowheads. (default=0)

.. attribute:: DimStyle.dxf.dimaltf

Alternate units dimension scale factor. (default=25.4)

.. attribute:: DimStyle.dxf.dimlfac

Scale factor for linear dimension values. (default=1)

.. attribute:: DimStyle.dxf.dimtvp

Vertical position of text above or below dimension line. (default=0)

.. attribute:: DimStyle.dxf.dimtfac

Scale factor for fractional or tolerance text size. (default=1)

.. attribute:: DimStyle.dxf.dimgap

Gap size between dimension line and dimension text. (default imperial=0.09, default metric=0.625)

.. attribute:: DimStyle.dxf.dimaltrnd

Rounding value for alternate dimension units. (default=0)

.. attribute:: DimStyle.dxf.dimtol

Toggles creation of appended tolerance dimensions. (default imperial=1, default metric=0)

.. attribute:: DimStyle.dxf.dimlim

Toggles creation of limits-style dimension text. (default=0)

.. attribute:: DimStyle.dxf.dimtih

Orientation of text inside extension lines. (default imperial=1, default metric=0)

.. attribute:: DimStyle.dxf.dimtoh

Orientation of text outside extension lines. (default imperial=1, default metric=0)

.. attribute:: DimStyle.dxf.dimse1

Toggles suppression of first extension line. (default=0)

.. attribute:: DimStyle.dxf.dimse2

Toggles suppression of second extension line. (default=0)

.. attribute:: DimStyle.dxf.dimtad

Sets text placement relative to dimension line. (default imperial=0, default metric=1)

.. attribute:: DimStyle.dxf.dimzin

Zero suppression for primary units dimensions. (default imperial=0, default metric=8) ???

.. attribute:: DimStyle.dxf.dimazin

Controls zero suppression for angular dimensions. (default=0)

.. attribute:: DimStyle.dxf.dimalt

Enables or disables alternate units dimensioning. (default=0)

.. attribute:: DimStyle.dxf.dimaltd

Controls decimal places for alternate units dimensions. (default imperial=2, default metric=3)

.. attribute:: DimStyle.dxf.dimtofl

Toggles forced dimension line creation. (default imperial=0, default metric=1)

.. attribute:: DimStyle.dxf.dimsah

Toggles appearance of arrowhead blocks. (default=0)

.. attribute:: DimStyle.dxf.dimtix

Toggles forced placement of text between extension lines. (default=0)

.. attribute:: DimStyle.dxf.dimsoxd

Suppresses dimension lines outside extension lines. (default=0)

.. attribute:: DimStyle.dxf.dimclrd

Dimension line, arrowhead, and leader line color. (default=0)

.. attribute:: DimStyle.dxf.dimclre

Dimension extension line color. (default=0)

.. attribute:: DimStyle.dxf.dimclrt

Dimension text color. (default=0)

.. attribute:: DimStyle.dxf.dimadec

Controls the number of decimal places for angular dimensions.

.. attribute:: DimStyle.dxf.dimunit

Obsolete, now use DIMLUNIT AND DIMFRAC

.. attribute:: DimStyle.dxf.dimdec

Decimal places for dimension values. (default imperial=4, default metric=2)

.. attribute:: DimStyle.dxf.dimtdec

Decimal places for primary units tolerance values. (default imperial=4, default metric=2)

.. attribute:: DimStyle.dxf.dimaltu

Units format for alternate units dimensions. (default=2)

.. attribute:: DimStyle.dxf.dimalttd

Decimal places for alternate units tolerance values. (default imperial=4, default metric=2)

.. attribute:: DimStyle.dxf.dimaunit

Unit format for angular dimension values. (default=0)

.. attribute:: DimStyle.dxf.dimfrac

Controls the fraction format used for architectural and fractional dimensions. (default=0)

.. attribute:: DimStyle.dxf.dimlunit

Specifies units for all nonangular dimensions. (default=2)

.. attribute:: DimStyle.dxf.dimdsep

Specifies a single character to use as a decimal separator. (default imperial=".", default metric=",")

.. attribute:: DimStyle.dxf.dimtmove

Controls the format of dimension text when it is moved. (default=0)

.. attribute:: DimStyle.dxf.dimjust

Horizontal justification of dimension text. (default=0)

.. attribute:: DimStyle.dxf.dimsd1

Toggles suppression of first dimension line. (default=0)

.. attribute:: DimStyle.dxf.dimsd2

Toggles suppression of second dimension line. (default=0)

.. attribute:: DimStyle.dxf.dimtolj

Vertical justification for dimension tolerance text. (default=1)

.. attribute:: DimStyle.dxf.dimaltz

Zero suppression for alternate units dimension values. (default=0)

.. attribute:: DimStyle.dxf.dimalttz

Zero suppression for alternate units tolerance values. (default=0)

.. attribute:: DimStyle.dxf.dimfit

Obsolete, now use DIMATFIT and DIMTMOVE

.. attribute:: DimStyle.dxf.dimupt

Controls user placement of dimension line and text. (default=0)

.. attribute:: DimStyle.dxf.dimatfit

Controls placement of text and arrowheads when there is insufficient space between the extension lines. (default=3)

.. attribute:: DimStyle.dxf.dimtxsty

Text style used for dimension text by name.

.. attribute:: DimStyle.dxf.dimtxsty_handle

Text style used for dimension text by handle of STYLE entry.
(use :attr:`DimStyle.dxf.dimtxsty` to get/set text style by name)

.. attribute:: DimStyle.dxf.dimldrblk

Specify arrowhead used for leaders by name.

.. attribute:: DimStyle.dxf.dimldrblk_handle

Specify arrowhead used for leaders by handle of referenced block.
(use :attr:`DimStyle.dxf.dimldrblk` to get/set arrowhead by name)

.. attribute:: DimStyle.dxf.dimblk_handle

Block type to use for both arrowheads, handle of referenced block.
(use :attr:`DimStyle.dxf.dimblk` to get/set arrowheads by name)

.. attribute:: DimStyle.dxf.dimblk1_handle

Block type to use for first arrowhead, handle of referenced block.
(use :attr:`DimStyle.dxf.dimblk1` to get/set arrowhead by name)

.. attribute:: DimStyle.dxf.dimblk2_handle

Block type to use for second arrowhead, handle of referenced block.
(use :attr:`DimStyle.dxf.dimblk2` to get/set arrowhead by name)

.. attribute:: DimStyle.dxf.dimlwd

Lineweight value for dimension lines. (default=-2, BYBLOCK)

.. attribute:: DimStyle.dxf.dimlwe

Lineweight value for extension lines. (default=-2, BYBLOCK)

.. attribute:: DimStyle.dxf.dimltype

Specifies the linetype used for the dimension line as linetype name, requires DXF R2007+

.. attribute:: DimStyle.dxf.dimltype_handle

Specifies the linetype used for the dimension line as handle to LTYPE entry, requires DXF R2007+
(use :attr:`DimStyle.dxf.dimltype` to get/set linetype by name)

.. attribute:: DimStyle.dxf.dimltex1

Specifies the linetype used for the extension line 1 as linetype name, requires DXF R2007+

.. attribute:: DimStyle.dxf.dimlex1_handle

Specifies the linetype used for the extension line 1 as handle to LTYPE entry, requires DXF R2007+
(use :attr:`DimStyle.dxf.dimltex1` to get/set linetype by name)

.. attribute:: DimStyle.dxf.dimltex2

Specifies the linetype used for the extension line 2 as linetype name, requires DXF R2007+

.. attribute:: DimStyle.dxf.dimlex2_handle

Specifies the linetype used for the extension line 2 as handle to LTYPE entry, requires DXF R2007+
(use :attr:`DimStyle.dxf.dimltex2` to get/set linetype by name)