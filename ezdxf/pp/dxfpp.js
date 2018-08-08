/* content of dxf2html.js */

TOOLTIPS= [];

function setUp(){
    initTooltips();
    setDXFTagTooltips();
}

function initTooltips(){
    var data = [
        [0, 0, "Text string indicating the entity type (fixed)"],
        [1, 1, "Primary text value for an entity"],
        [2, 2, "Name (attribute tag, block name, and so on)"],
        [3, 4, "Other text or name values"],
        [5, 5, "Entity handle; text string of up to 16 hexadecimal digits (fixed)"],
        [6, 6, "Linetype name (fixed)"],
        [7, 7, "Text style name (fixed)"],
        [8, 8, "Layer name (fixed)"],
        [9, 9, "DXF: variable name identifier (used only in HEADER section of the DXF file)"],
        [10, 10, "Primary point; this is the start point of a line or text entity, center of a circle, and so on " +
          "DXF: X value of the primary point (followed by Y and Z value codes 20 and 30) " +
          "APP: 3D point (list of three reals)"],
        [11, 18, "Other points " +
          "DXF: X value of other points (followed by Y value codes 21-28 and Z value codes 31-38) " +
          "APP: 3D point (list of three reals)"],
        [20, 20, "DXF: Y value of the primary point"],
        [30, 30, "DXF: Z value of the primary point"],
        [21, 28, "DXF: Y values of other points"],
        [31, 37, "DXF: Z values of other points"],
        [38, 38, "DXF: entity's elevation if nonzero"],
        [39, 39, "Entity's thickness if nonzero (fixed)"],
        [40, 47, "Double-precision floating-point values (text height, scale factors, and so on)"],
        [48, 48, "Linetype scale; default value is defined for all entity types"],
        [49, 49, "Multiple 49 groups may appear in one entity for variable-length tables (such as " +
          "the dash lengths in the LTYPE table). A 7x group always appears before the first 49 group " +
          "to specify the table length"],
        [50, 58, "Angles (output in degrees to DXF files and radians through AutoLISP and ObjectARX applications)"],
        [60, 60, "Entity visibility; absence or 0 indicates visibility; 1 indicates invisibility"],
        [62, 62, "Color number (fixed)"],
        [66, 66, "Entities follow flag (fixed)"],
        [67, 67, "0 for model space or 1 for paper space (fixed)"],
        [68, 68, "APP: identifies whether viewport is on but fully off screen; is not active or is off"],
        [69, 69, "APP: viewport identification number"],
        [70, 79, "Integer values, such as repeat counts, flag bits, or modes"],
        [90, 99, "32-bit integer values"],
        [100, 100, "Subclass data marker (with derived class name as a string). Required for all objects and entity " +
          "classes that are derived from another concrete class. The subclass data marker segregates data " +
          "defined by different classes in the inheritance chain for the same object. " +
          "This is in addition to the requirement for DXF names for each distinct concrete class derived " +
          "from ObjectARX (see Subclass Markers)"],
        [101, 101, "Embedded object marker"],
        [102, 102, "Control string, followed by '{arbitrary name' or '}'. " +
          "Similar to the xdata 1002 group code, except that when the string begins with '{', " +
          "it can be followed by an arbitrary string whose interpretation is up to the application. " +
          "The only other control string allowed is &quot;}&quot; as a group terminator. " +
          "AutoCAD does not interpret these strings except during drawing audit operations. " +
          "They are for application use."],
        [105, 105, "Object handle for DIMVAR symbol table entry"],
        [110, 110, "UCS origin (appears only if code 72 is set to 1); DXF: X value; APP: 3D point"],
        [111, 111, "UCS Y-axis (appears only if code 72 is set to 1); DXF: Y value; APP: 3D vector"],
        [112, 112, "UCS Z-axis (appears only if code 72 is set to 1); DXF: Z value; APP: 3D vector"],
        [120, 122, "DXF: Y value of UCS origin, UCS X-axis, and UCS Y-axis"],
        [130, 132, "DXF: Z value of UCS origin, UCS X-axis, and UCS Y-axis"],
        [140, 149, "Double-precision floating-point values (points, elevation, and DIMSTYLE settings, for example)"],
        [170, 179, "16-bit integer values, such as flag bits representing DIMSTYLE settings"],
        [210, 210, "Extrusion direction (fixed) " +
          "DXF: X value of extrusion direction " +
          "APP: 3D extrusion direction vector"],
        [220, 220, "DXF: Y value of the extrusion direction"],
        [230, 230, "DXF: Z value of the extrusion direction"],
        [270, 279, "16-bit integer values"],
        [280, 289, "16-bit integer value"],
        [290, 299, "Boolean flag value; 0 = False; 1 = True"],
        [300, 309, "Arbitrary text strings"],
        [310, 319, "Arbitrary binary chunks with same representation and limits " +
          "as 1004 group codes: hexadecimal strings of up to 254 characters " +
          "represent data chunks of up to 127 bytes"],
        [320, 329, "Arbitrary object handles; handle values that are taken 'as is'. " +
          "They are not translated during INSERT and XREF operations"],
        [330, 339, "Soft-pointer handle; arbitrary soft pointers to other objects " +
          "within same DXF file or drawing. Translated during INSERT and XREF operations"],
        [340, 349, "Hard-pointer handle; arbitrary hard pointers to other objects within " +
          "same DXF file or drawing. Translated during INSERT and XREF operations"],
        [350, 359, "Soft-owner handle; arbitrary soft ownership links to other objects " +
          "within same DXF file or drawing. Translated during INSERT and XREF operations"],
        [360, 369, "Hard-owner handle; arbitrary hard ownership links to other objects within " +
          "same DXF file or drawing. Translated during INSERT and XREF operations"],
        [370, 379, "Lineweight enum value (AcDb::LineWeight). Stored and moved around as a 16-bit integer. " +
          "Custom non-entity objects may use the full range, but entity classes only use 371-379 DXF " +
          "group codes in their representation, because AutoCAD and AutoLISP both always assume a 370 " +
          "group code is the entity's lineweight. This allows 370 to behave like other 'common' entity fields"],
        [380, 389, "PlotStyleName type enum (AcDb::PlotStyleNameType). Stored and moved around as a 16-bit integer. " +
          "Custom non-entity objects may use the full range, but entity classes only use 381-389 " +
          "DXF group codes in their representation, for the same reason as the lineweight range"],
        [390, 399, "String representing handle value of the PlotStyleName object, basically a hard pointer, but has " +
          "a different range to make backward compatibility easier to deal with. Stored and moved around " +
          "as an object ID (a handle in DXF files) and a special type in AutoLISP. Custom non-entity objects " +
          "may use the full range, but entity classes only use 391-399 DXF group codes in their representation, " +
          "for the same reason as the lineweight range"],
        [400, 409, "16-bit integers"],
        [410, 419, "String"],
        [420, 427, "32-bit integer value. When used with True Color; a 32-bit integer representing a 24-bit color value. " +
          "The high-order byte (8 bits) is 0, the low-order byte an unsigned char holding the Blue value (0-255), " +
          "then the Green value, and the next-to-high order byte is the Red Value. Converting this integer value to " +
          "hexadecimal yields the following bit mask: 0x00RRGGBB. " +
          "For example, a true color with Red==200, Green==100 and Blue==50 is 0x00C86432, and in DXF, in decimal, 13132850"],
        [430, 437, "String; when used for True Color, a string representing the name of the color"],
        [440, 447, "32-bit integer value. When used for True Color, the transparency value"],
        [450, 459, "Long"],
        [460, 469, "Double-precision floating-point value"],
        [470, 479, "String"],
        [480, 481, "Hard-pointer handle; arbitrary hard pointers to other objects within same DXF file or drawing. " +
          "Translated during INSERT and XREF operations"],
        [999, 999, "DXF: The 999 group code indicates that the line following it is a comment string. SAVEAS does " +
          "not include such groups in a DXF output file, but OPEN honors them and ignores the comments. " +
          "You can use the 999 group to include comments in a DXF file that you have edited"],
        [1000, 1000, "ASCII string (up to 255 bytes long) in extended data"],
        [1001, 1001, "Registered application name (ASCII string up to 31 bytes long) for extended data"],
        [1002, 1002, "Extended data control string ('{' or '}')"],
        [1003, 1003, "Extended data layer name"],
        [1004, 1004, "Chunk of bytes (up to 127 bytes long) in extended data"],
        [1005, 1005, "Entity handle in extended data; text string of up to 16 hexadecimal digits"],
        [1010, 1010, "A point in extended data; DXF: X value (followed by 1020 and 1030 groups); APP: 3D point"],
        [1020, 1020, "DXF: Y values of a point"],
        [1030, 1030, "DXF: Z values of a point"],
        [1011, 1011, "A 3D world space position in extended data \n" +
            "DXF: X value (followed by 1021 and 1031 groups) \n" +
            "APP: 3D point"],
        [1021, 1021, "DXF: Y value of a world space position"],
        [1031, 1031, "DXF: Z value of a world space position"],
        [1012, 1012, "A 3D world space displacement in extended data \n" +
            "DXF: X value (followed by 1022 and 1032 groups) \n" +
            "APP: 3D vector"],
        [1022, 1022, "DXF: Y value of a world space displacement"],
        [1032, 1032, "DXF: Z value of a world space displacement"],
        [1013, 1013, "A 3D world space direction in extended data \n" +
          "DXF: X value (followed by 1022 and 1032 groups) \n" +
          "APP: 3D vector"],
        [1023, 1023, "DXF: Y value of a world space direction"],
        [1033, 1033, "DXF: Z value of a world space direction"],
        [1040, 1040, "Extended data double-precision floating-point value"],
        [1041, 1041, "Extended data distance value"],
        [1042, 1042, "Extended data scale factor"],
        [1070, 1070, "Extended data 16-bit signed integer"],
        [1071, 1071, "Extended data 32-bit signed long"]
    ];
    var startIndex, endIndex, text;
    for (var i=0; i<data.length; i++){
        var row = data[i];
        startIndex = row[0];
        endIndex = row[1];
        text = row[2];
        for(var j=startIndex; j<=endIndex; j++){
            TOOLTIPS[j] = text;
        }
    }
}

function getCode(node){
    return parseInt(node.firstChild.textContent);
}

function setDXFTagTooltips() {
    var tags = document.getElementsByClassName("dxf-tag");
    var tag, code;
    for (var i = 0; i < tags.length; i++) {
        tag = tags[i];
        code = getCode(tag);
        tag.title = TOOLTIPS[code];
    }
}
