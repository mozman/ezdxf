.. _file structure:

DXF File Structure
------------------

A Drawing Interchange File is simply an ASCII text file with a file
type of .dxf and specially formatted text. The overall organization
of a DXF file is as follows:

1. HEADER - General information about the drawing is found
   in this section of the DXF file. Each parameter has a variable
   name and an associated value.

2. CLASSES - This section holds the information for application-defined
   classes. This section was introduced with AC1015 and can usually be
   ignored.

3. TABLES - This section contains definitions of named items.

   * Linetype table (LTYPE)
   * Layer table (LAYER)
   * Text Style table (STYLE)
   * View table (VIEW)
   * User Coordinate System table (UCS)
   * Viewport configuration table (VPORT)
   * Dimension Style table (DIMSTYLE)
   * Application Identification table (APPID)

4. BLOCKS - This section contains Block Definition entities
   describing the entities that make up each Block in the drawing.

5. ENTITIES - This section contains the drawing entities,
   including any Block References.

6. OBJECTS - non-graphical objects

7. THUMBNAILIMAGE - This section contains a preview image of the DXF
   file, it is optional and can usually be ignored.

8. END OF FILE

By using *ezdxf* you don't have to know much about this details, but
interested users can look at the original `DXF Reference`_.

.. _DXF Reference: http://docs.autodesk.com/ACD/2014/ENU/index.html?url=files/GUID-235B22E0-A567-4CF6-92D3-38A2306D73F3.htm,topicNumber=d30e652301