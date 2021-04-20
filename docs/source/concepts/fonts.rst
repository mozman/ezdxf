.. _font resources:

Font Resources
--------------

DXF relies on the infrastructure installed by AutoCAD like the included SHX
files or True Type fonts. There is no simple way to store additional information
about a used fonts beside the plain file system name like ``"arial.ttf"``.
The CAD application or viewer which opens the DXF file has to have access to
the specified fonts used in your DXF document or it has to use an appropriate
replacement font, which is not that easy in the age of unicode. Later DXF
versions can store font family names in the XDATA of the STYLE entity but not
all CAD application use this information.
