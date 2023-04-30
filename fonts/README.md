Font Resources
==============

TrueType Fonts
--------------

The TrueType fonts in this folder have liberal licences, so it is possible to 
include them in a public repository. These fonts are used for tests by the `ezdxf` 
package on every system the tests can run (Windows, Linux <on github>, macOS).

Shapefiles
----------

The font-manager also scans the folders recursively for .shx, .shp and 
.lff fonts - the basic stroke fonts included in CAD applications.
The .shx and .shp fonts are copyright protected and cannot be included in a public 
github repository. 

The LibreCAD .lff fonts are free but licensed under the "GPL v2 or later" and therefore
are a problem for users who want to modify the `ezdxf` package (MIT licensed) without 
publishing these modifications. Maybe this would be legal, but I don't read 
"thousands" of FAQs to understand this license.
