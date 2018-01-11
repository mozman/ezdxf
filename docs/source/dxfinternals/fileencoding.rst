.. _DXF File Encoding:

DXF File Encoding
=================

DXF Version R2004 and prior
---------------------------

Drawing files of DXF versions R2004 (AC1018) and prior are saved as ASCII files with the encoding set by the header
variable *$DWGCODEPAGE*, which is ANSI_1252 by default if *$DWGCODEPAGE* is not set.

Characters used in the drawing which do not exist in the chosen ASCII encoding are encoded as unicode characters with
the schema ``\U+nnnn``. see `Unicode table`_

Known *$DWGCODEPAGE* encodings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

========= ====== ================
DXF       Python Name
========= ====== ================
ANSI_874  cp874  Thai
ANSI_932  cp932  Japanese
ANSI_936  gbk    UnifiedChinese
ANSI_949  cp949  Korean
ANSI_950  cp950  TradChinese
ANSI_1250 cp1250 CentralEurope
ANSI_1251 cp1251 Cyrillic
ANSI_1252 cp1252 WesternEurope
ANSI_1253 cp1253 Greek
ANSI_1254 cp1254 Turkish
ANSI_1255 cp1255 Hebrew
ANSI_1256 cp1256 Arabic
ANSI_1257 cp1257 Baltic
ANSI_1258 cp1258 Vietnam
========= ====== ================

DXF Version R2007 and later
---------------------------

Starting with DXF version R2007 (AC1021) the drawing file is encoded by UTF-8, the header variable
*$DWGCODEPAGE* is still in use, but I don't know, if the setting still has any meaning.

Encoding characters in the unicode schema ``\U+nnnn`` is still functional.

.. seealso::

    :ref:`String Value Encoding`

.. _Unicode Table: http://unicode-table.com/en/