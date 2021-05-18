# Copyright (c) 2011-2020, Manfred Moitzi
# License: MIT License
from enum import IntEnum, IntFlag

DXF9 = 'AC1004'
DXF10 = 'AC1006'
DXF12 = 'AC1009'
DXF13 = 'AC1012'
DXF14 = 'AC1014'
DXF2000 = 'AC1015'
DXF2004 = 'AC1018'
DXF2007 = 'AC1021'
DXF2010 = 'AC1024'
DXF2013 = 'AC1027'
DXF2018 = 'AC1032'

acad_release = {
    DXF9: 'R9',
    DXF10: 'R10',
    DXF12: 'R12',
    DXF13: 'R13',
    DXF14: 'R14',
    DXF2000: 'R2000',
    DXF2004: 'R2004',
    DXF2007: 'R2007',
    DXF2010: 'R2010',
    DXF2013: 'R2013',
    DXF2018: 'R2018',
}

acad_maint_ver = {
    DXF12: 0,
    DXF2000: 6,
    DXF2004: 0,
    DXF2007: 25,
    DXF2010: 6,
    DXF2013: 105,
    DXF2018: 4,
}

versions_supported_by_new = [
    DXF12, DXF2000, DXF2004, DXF2007, DXF2010, DXF2013, DXF2018]
versions_supported_by_save = versions_supported_by_new
LATEST_DXF_VERSION = versions_supported_by_new[-1]

acad_release_to_dxf_version = {
    acad: dxf for dxf, acad in acad_release.items()
}


class DXFError(Exception):
    pass


class InvalidGeoDataException(DXFError):
    pass


class DXFStructureError(DXFError):
    pass


class DXFAppDataError(DXFStructureError):
    pass


class DXFXDataError(DXFStructureError):
    pass


class DXFVersionError(DXFError):
    """ Errors related to features not supported by the chosen DXF Version """
    pass


class DXFInternalEzdxfError(DXFError):
    """ Indicates internal errors -  should be fixed by mozman """
    pass


class DXFUnsupportedFeature(DXFError):
    """ Indicates unsupported features for DXFEntities e.g. translation for
    ACIS data
    """
    pass


class DXFValueError(DXFError, ValueError):
    pass


class DXFKeyError(DXFError, KeyError):
    pass


class DXFAttributeError(DXFError, AttributeError):
    pass


class DXFIndexError(DXFError, IndexError):
    pass


class DXFTypeError(DXFError, TypeError):
    pass


class DXFTableEntryError(DXFValueError):
    pass


class DXFEncodingError(DXFError):
    pass


class DXFDecodingError(DXFError):
    pass


class DXFInvalidLineType(DXFValueError):
    pass


class DXFBlockInUseError(DXFValueError):
    pass


class DXFUndefinedBlockError(DXFKeyError):
    pass


MANAGED_SECTIONS = {
    'HEADER', 'CLASSES', 'TABLES', 'BLOCKS', 'ENTITIES', 'OBJECTS', 'ACDSDATA'
}

TABLE_NAMES_ACAD_ORDER = [
    'VPORT',
    'LTYPE',
    'LAYER',
    'STYLE',
    'VIEW',
    'UCS',
    'APPID',
    'DIMSTYLE',
    'BLOCK_RECORD',
]

APP_DATA_MARKER = 102
SUBCLASS_MARKER = 100
XDATA_MARKER = 1001
COMMENT_MARKER = 999
STRUCTURE_MARKER = 0
HEADER_VAR_MARKER = 9
ACAD_REACTORS = '{ACAD_REACTORS'
ACAD_XDICTIONARY = '{ACAD_XDICTIONARY'
XDICT_HANDLE_CODE = 360
REACTOR_HANDLE_CODE = 330
OWNER_CODE = 330

# Special tag codes for internal purpose:
# -1 to -5 id reserved by AutoCAD for internal use, but this tags will never be
# saved to file.
# Same approach here, the following tags have to be converted/transformed into
# normal tags before saved to file.
COMPRESSED_TAGS = -10

BYBLOCK = 0
BYLAYER = 256
BYOBJECT = 257
RED = 1
YELLOW = 2
GREEN = 3
CYAN = 4
BLUE = 5
MAGENTA = 6
BLACK = 7
WHITE = 7


class ACI(IntEnum):
    BYBLOCK = 0
    BYLAYER = 256
    BYOBJECT = 257
    RED = 1
    YELLOW = 2
    GREEN = 3
    CYAN = 4
    BLUE = 5
    MAGENTA = 6
    BLACK = 7
    WHITE = 7


LINEWEIGHT_BYLAYER = -1
LINEWEIGHT_BYBLOCK = -2
LINEWEIGHT_DEFAULT = -3

VALID_DXF_LINEWEIGHTS = (
    0, 5, 9, 13, 15, 18, 20, 25, 30, 35, 40, 50, 53, 60, 70, 80, 90,
    100, 106, 120, 140, 158, 200, 211,
)
MAX_VALID_LINEWEIGHT = VALID_DXF_LINEWEIGHTS[-1]
VALID_DXF_LINEWEIGHT_VALUES = set(VALID_DXF_LINEWEIGHTS) | {
    LINEWEIGHT_DEFAULT, LINEWEIGHT_BYLAYER, LINEWEIGHT_BYBLOCK}

# Entity: Polyline, Polymesh
# 70 flags
POLYLINE_CLOSED = 1
POLYLINE_MESH_CLOSED_M_DIRECTION = POLYLINE_CLOSED
POLYLINE_CURVE_FIT_VERTICES_ADDED = 2
POLYLINE_SPLINE_FIT_VERTICES_ADDED = 4
POLYLINE_3D_POLYLINE = 8
POLYLINE_3D_POLYMESH = 16
POLYLINE_MESH_CLOSED_N_DIRECTION = 32
POLYLINE_POLYFACE = 64
POLYLINE_GENERATE_LINETYPE_PATTERN = 128

# Entity: Polymesh
# 75 surface smooth type
POLYMESH_NO_SMOOTH = 0
POLYMESH_QUADRATIC_BSPLINE = 5
POLYMESH_CUBIC_BSPLINE = 6
POLYMESH_BEZIER_SURFACE = 8

# Entity: Vertex
# 70 flags
VERTEXNAMES = ('vtx0', 'vtx1', 'vtx2', 'vtx3')
VTX_EXTRA_VERTEX_CREATED = 1  # Extra vertex created by curve-fitting
VTX_CURVE_FIT_TANGENT = 2  # Curve-fit tangent defined for this vertex.
# A curve-fit tangent direction of 0 may be omitted from the DXF output, but is
# significant if this bit is set.
# 4 = unused, never set in dxf files
VTX_SPLINE_VERTEX_CREATED = 8  # Spline vertex created by spline-fitting
VTX_SPLINE_FRAME_CONTROL_POINT = 16
VTX_3D_POLYLINE_VERTEX = 32
VTX_3D_POLYGON_MESH_VERTEX = 64
VTX_3D_POLYFACE_MESH_VERTEX = 128

VERTEX_FLAGS = {
    'AcDb2dPolyline': 0,
    'AcDb3dPolyline': VTX_3D_POLYLINE_VERTEX,
    'AcDbPolygonMesh': VTX_3D_POLYGON_MESH_VERTEX,
    'AcDbPolyFaceMesh': VTX_3D_POLYGON_MESH_VERTEX | VTX_3D_POLYFACE_MESH_VERTEX,
}
POLYLINE_FLAGS = {
    'AcDb2dPolyline': 0,
    'AcDb3dPolyline': POLYLINE_3D_POLYLINE,
    'AcDbPolygonMesh': POLYLINE_3D_POLYMESH,
    'AcDbPolyFaceMesh': POLYLINE_POLYFACE,
}

# block-type flags (bit coded values, may be combined):
# Entity: BLOCK
# 70 flags

# This is an anonymous block generated by hatching, associative dimensioning,
# other internal operations, or an application:
BLK_ANONYMOUS = 1

# This block has non-constant attribute definitions (this bit is not set if the
# block has any attribute definitions that are constant, or has no attribute
# definitions at all)
BLK_NON_CONSTANT_ATTRIBUTES = 2

# This block is an external reference (xref):
BLK_XREF = 4

# This block is an xref overlay:
BLK_XREF_OVERLAY = 8

# This block is externally dependent:
BLK_EXTERNAL = 16

# This is a resolved external reference, or dependent of an external reference
# (ignored on input):
BLK_RESOLVED = 32

# This definition is a referenced external reference (ignored on input):
BLK_REFERENCED = 64

LWPOLYLINE_CLOSED = 1
LWPOLYLINE_PLINEGEN = 128

TEXT_ALIGN_FLAGS = {
    'LEFT': (0, 0),
    'CENTER': (1, 0),
    'RIGHT': (2, 0),
    'ALIGNED': (3, 0),
    'MIDDLE': (4, 0),
    'FIT': (5, 0),
    'BOTTOM_LEFT': (0, 1),
    'BOTTOM_CENTER': (1, 1),
    'BOTTOM_RIGHT': (2, 1),
    'MIDDLE_LEFT': (0, 2),
    'MIDDLE_CENTER': (1, 2),
    'MIDDLE_RIGHT': (2, 2),
    'TOP_LEFT': (0, 3),
    'TOP_CENTER': (1, 3),
    'TOP_RIGHT': (2, 3),
}
TEXT_ALIGNMENT_BY_FLAGS = dict(
    (flags, name) for name, flags in TEXT_ALIGN_FLAGS.items()
)

LEFT = 0
CENTER = 1
RIGHT = 2
ALIGNED = 3
# MIDDLE = 4
FIT = 5

BASELINE = 0
BOTTOM = 1
MIDDLE = 2
TOP = 3
MIRROR_X = 2
BACKWARD = MIRROR_X
MIRROR_Y = 4
UPSIDE_DOWN = MIRROR_Y

VERTICAL_STACKED = 4  # only stored in TextStyle.dxf.flags!

# Special char and encodings used in TEXT, ATTRIB and ATTDEF:
# "%%d" -> "°"
SPECIAL_CHAR_ENCODING = {
    'c': 'Ø',  # alt-0216
    'd': '°',  # alt-0176
    'p': '±',  # alt-0177
}
# Inline codes for strokes in TEXT, ATTRIB and ATTDEF
# %%u underline
# %%o overline
# %%k strike through
# Formatting will be applied until the same code appears again or the end
# of line.
# Special codes and formatting is case insensitive: d=D, u=U

MTEXT_TOP_LEFT = 1
MTEXT_TOP_CENTER = 2
MTEXT_TOP_RIGHT = 3
MTEXT_MIDDLE_LEFT = 4
MTEXT_MIDDLE_CENTER = 5
MTEXT_MIDDLE_RIGHT = 6
MTEXT_BOTTOM_LEFT = 7
MTEXT_BOTTOM_CENTER = 8
MTEXT_BOTTOM_RIGHT = 9

MTEXT_ALIGN_FLAGS = {
    'TOP_LEFT': 1,
    'TOP_CENTER': 2,
    'TOP_RIGHT': 3,
    'MIDDLE_LEFT': 4,
    'MIDDLE_CENTER': 5,
    'MIDDLE_RIGHT': 6,
    'BOTTOM_LEFT': 7,
    'BOTTOM_CENTER': 8,
    'BOTTOM_RIGHT': 9,
}


class MTextEntityAlignment(IntEnum):
    TOP_LEFT = MTEXT_TOP_LEFT
    TOP_CENTER = MTEXT_TOP_CENTER
    TOP_RIGHT = MTEXT_TOP_RIGHT
    MIDDLE_LEFT = MTEXT_MIDDLE_LEFT
    MIDDLE_CENTER = MTEXT_MIDDLE_CENTER
    MIDDLE_RIGHT = MTEXT_MIDDLE_RIGHT
    BOTTOM_LEFT = MTEXT_BOTTOM_LEFT
    BOTTOM_CENTER = MTEXT_BOTTOM_CENTER
    BOTTOM_RIGHT = MTEXT_BOTTOM_RIGHT


class MTextParagraphAlignment(IntEnum):
    DEFAULT = 0
    LEFT = 1
    RIGHT = 2
    CENTER = 3
    JUSTIFIED = 4
    DISTRIBUTED = 5


MTEXT_LEFT_TO_RIGHT = 1
MTEXT_TOP_TO_BOTTOM = 3
MTEXT_BY_STYLE = 5


class MTextFlowDirection(IntEnum):
    LEFT_TO_RIGHT = MTEXT_LEFT_TO_RIGHT
    TOP_TO_BOTTOM = MTEXT_TOP_TO_BOTTOM
    BY_STYLE = MTEXT_BY_STYLE


class MTextLineAlignment(IntEnum):  # exclusive state
    BOTTOM = 0
    MIDDLE = 1
    TOP = 2


class MTextStroke(IntFlag):  # Combination of flags is possible
    UNDERLINE = 1
    STRIKE_THROUGH = 2
    OVERLINE = 4


MTEXT_AT_LEAST = 1
MTEXT_EXACT = 2


class MTextLineSpacing(IntEnum):
    AT_LEAST = MTEXT_AT_LEAST
    EXACT = MTEXT_EXACT


MTEXT_COLOR_INDEX = {
    'red': RED,
    'yellow': YELLOW,
    'green': GREEN,
    'cyan': CYAN,
    'blue': BLUE,
    'magenta': MAGENTA,
    'white': WHITE,
}

MTEXT_BG_OFF = 0
MTEXT_BG_COLOR = 1
MTEXT_BG_WINDOW_COLOR = 2
MTEXT_BG_CANVAS_COLOR = 3
MTEXT_TEXT_FRAME = 16


class MTextBackgroundColor(IntEnum):
    OFF = MTEXT_BG_OFF
    COLOR = MTEXT_BG_COLOR
    WINDOW = MTEXT_BG_WINDOW_COLOR
    CANVAS = MTEXT_BG_CANVAS_COLOR


MTEXT_INLINE_ALIGN = {
    'BOTTOM': MTextLineAlignment.BOTTOM,
    'MIDDLE': MTextLineAlignment.MIDDLE,
    'TOP': MTextLineAlignment.TOP,
}

CLOSED_SPLINE = 1
PERIODIC_SPLINE = 2
RATIONAL_SPLINE = 4
PLANAR_SPLINE = 8
LINEAR_SPLINE = 16

# Hatch constants
HATCH_TYPE_USER_DEFINED = 0
HATCH_TYPE_PREDEFINED = 1
HATCH_TYPE_CUSTOM = 2

HATCH_STYLE_NORMAL = 0
HATCH_STYLE_NESTED = 0
HATCH_STYLE_OUTERMOST = 1
HATCH_STYLE_IGNORE = 2

BOUNDARY_PATH_DEFAULT = 0
BOUNDARY_PATH_EXTERNAL = 1
BOUNDARY_PATH_POLYLINE = 2
BOUNDARY_PATH_DERIVED = 4
BOUNDARY_PATH_TEXTBOX = 8
BOUNDARY_PATH_OUTERMOST = 16

GRADIENT_TYPES = frozenset([
    'LINEAR',
    'CYLINDER',
    'INVCYLINDER',
    'SPHERICAL',
    'INVSPHERICAL',
    'HEMISPHERICAL',
    'INVHEMISPHERICAL',
    'CURVED',
    'INVCURVED'
])

# Viewport Status Flags (VSF) group code=90
VSF_PERSPECTIVE_MODE = 0x1  # enabled if set
VSF_FRONT_CLIPPING = 0x2  # enabled if set
VSF_BACK_CLIPPING = 0x4  # enabled if set
VSF_USC_FOLLOW = 0x8  # enabled if set
VSF_FRONT_CLIPPING_NOT_AT_EYE = 0x10  # enabled if set
VSF_UCS_ICON_VISIBILITY = 0x20  # enabled if set
VSF_UCS_ICON_AT_ORIGIN = 0x40  # enabled if set
VSF_FAST_ZOOM = 0x80  # enabled if set
VSF_SNAP_MODE = 0x100  # enabled if set
VSF_GRID_MODE = 0x200  # enabled if set
VSF_ISOMETRIC_SNAP_STYLE = 0x400  # enabled if set
VSF_HIDE_PLOT_MODE = 0x800  # enabled if set

# If set and kIsoPairRight is not set, then isopair top is enabled.
# If both kIsoPairTop and kIsoPairRight are set, then isopair left is enabled:
VSF_KISOPAIR_TOP = 0x1000

# If set and kIsoPairTop is not set, then isopair right is enabled:
VSF_KISOPAIR_RIGHT = 0x2000
VSF_VIEWPORT_ZOOM_LOCKING = 0x4000  # enabled if set
VSF_LOCK_ZOOM = 0x4000  # enabled if set
VSF_CURRENTLY_ALWAYS_ENABLED = 0x8000  # always set without a meaning :)
VSF_NON_RECTANGULAR_CLIPPING = 0x10000  # enabled if set
VSF_TURN_VIEWPORT_OFF = 0x20000
VSF_NO_GRID_LIMITS = 0x40000
VSF_ADAPTIVE_GRID_DISPLAY = 0x80000
VSF_SUBDIVIDE_GRID = 0x100000
VSF_GRID_FOLLOW_WORKPLANE = 0x200000

# Viewport Render Mode (VRM) group code=281
VRM_2D_OPTIMIZED = 0
VRM_WIREFRAME = 1
VRM_HIDDEN_LINE = 2
VRM_FLAT_SHADED = 3
VRM_GOURAUD_SHADED = 4
VRM_FLAT_SHADED_WITH_WIREFRAME = 5
VRM_GOURAUD_SHADED_WITH_WIREFRAME = 6

IMAGE_SHOW = 1
IMAGE_SHOW_WHEN_NOT_ALIGNED = 2
IMAGE_USE_CLIPPING_BOUNDARY = 4
IMAGE_TRANSPARENCY_IS_ON = 8

UNDERLAY_CLIPPING = 1
UNDERLAY_ON = 2
UNDERLAY_MONOCHROME = 4
UNDERLAY_ADJUST_FOR_BG = 8

DIM_LINEAR = 0
DIM_ALIGNED = 1
DIM_ANGULAR = 2
DIM_DIAMETER = 3
DIM_RADIUS = 4
DIM_ANGULAR_3P = 5
DIM_ORDINATE = 6
DIM_BLOCK_EXCLUSIVE = 32
DIM_ORDINATE_TYPE = 64
DIM_USER_LOCATION_OVERRIDE = 128

DIMZIN_SUPPRESS_ZERO_FEET_AND_PRECISELY_ZERO_INCHES = 0
DIMZIN_INCLUDES_ZERO_FEET_AND_PRECISELY_ZERO_INCHES = 1
DIMZIN_INCLUDES_ZERO_FEET_AND_SUPPRESSES_ZERO_INCHES = 2
DIMZIN_INCLUDES_ZERO_INCHES_AND_SUPPRESSES_ZERO_FEET = 3
DIMZIN_SUPPRESSES_LEADING_ZEROS = 4  # only decimal dimensions
DIMZIN_SUPPRESSES_TRAILING_ZEROS = 8  # only decimal dimensions

# ATTRIB & ATTDEF flags
ATTRIB_INVISIBLE = 1  # Attribute is invisible (does not appear)
ATTRIB_CONST = 2  # This is a constant attribute
ATTRIB_VERIFY = 4  # Verification is required on input of this attribute
ATTRIB_IS_PRESET = 8  # no prompt during insertion

# '|' is allowed in layer name, as ltype name ...
INVALID_NAME_CHARACTERS = '<>/\\":;?*=`'
INVALID_LAYER_NAME_CHARACTERS = set(INVALID_NAME_CHARACTERS)

STD_SCALES = {
    1: (1. / 128., 12.),
    2: (1. / 64., 12.),
    3: (1. / 32., 12.),
    4: (1. / 16., 12.),
    5: (3. / 32., 12.),
    6: (1. / 8., 12.),
    7: (3. / 16., 12.),
    8: (1. / 4., 12.),
    9: (3. / 8., 12.),
    10: (1. / 2., 12.),
    11: (3. / 4., 12.),
    12: (1., 12.),
    13: (3., 12.),
    14: (6., 12.),
    15: (12., 12.),
    16: (1., 1.),
    17: (1., 2.),
    18: (1., 4.),
    19: (1., 8.),
    20: (1., 10.),
    21: (1., 16.),
    22: (1., 20.),
    23: (1., 30.),
    24: (1., 40.),
    25: (1., 50.),
    26: (1., 100.),
    27: (2., 1.),
    28: (4., 1.),
    29: (8., 1.),
    30: (10., 1.),
    31: (100., 1.),
    32: (1000., 1.),
}

RASTER_UNITS = {
    'mm': 1,
    'cm': 2,
    'm': 3,
    'km': 4,
    'in': 5,
    'ft': 6,
    'yd': 7,
    'mi': 8,
}

MODEL_SPACE_R2000 = '*Model_Space'
MODEL_SPACE_R12 = '$Model_Space'
PAPER_SPACE_R2000 = '*Paper_Space'
PAPER_SPACE_R12 = '$Paper_Space'
TMP_PAPER_SPACE_NAME = '*Paper_Space999999'

MODEL_SPACE = {
    MODEL_SPACE_R2000.lower(),
    MODEL_SPACE_R12.lower(),
}

PAPER_SPACE = {
    PAPER_SPACE_R2000.lower(),
    PAPER_SPACE_R12.lower(),
}

LAYOUT_NAMES = {
    PAPER_SPACE_R2000.lower(),
    PAPER_SPACE_R12.lower(),
    MODEL_SPACE_R2000.lower(),
    MODEL_SPACE_R12.lower(),
}


class SortEntities:
    DISABLE = 0
    SELECTION = 1  # 1 = Sorts for object selection
    SNAP = 2  # 2 = Sorts for object snap
    REDRAW = 4  # 4 = Sorts for redraws; obsolete
    MSLIDE = 8  # 8 = Sorts for MSLIDE command slide creation; obsolete
    REGEN = 16  # 16 = Sorts for REGEN commands
    PLOT = 32  # 32 = Sorts for plotting
    POSTSCRIPT = 64  # 64 = Sorts for PostScript output; obsolete


DIMJUST = {
    'center': 0,
    'left': 1,
    'right': 2,
    'above1': 3,
    'above2': 4,
}

DIMTAD = {
    'above': 1,
    'center': 0,
    'below': 4,
}


class InsertUnits(IntEnum):
    Unitless = 0
    Inches = 1
    Feet = 2
    Miles = 3
    Millimeters = 4
    Centimeters = 5
    Meters = 6
    Kilometers = 7
    Microinches = 8
    Mils = 9
    Yards = 10
    Angstroms = 11
    Nanometers = 12
    Microns = 13
    Decimeters = 14
    Decameters = 15
    Hectometers = 16
    Gigameters = 17
    AstronomicalUnits = 18
    Lightyears = 19
    Parsecs = 20
    USSurveyFeet = 21
    USSurveyInch = 22
    USSurveyYard = 23
    USSurveyMile = 24


DEFAULT_ENCODING = 'cp1252'

MLINE_TOP = 0
MLINE_ZERO = 1
MLINE_BOTTOM = 2
MLINE_HAS_VERTICES = 1
MLINE_CLOSED = 2
MLINE_SUPPRESS_START_CAPS = 4
MLINE_SUPPRESS_END_CAPS = 8

MLINESTYLE_FILL = 1
MLINESTYLE_MITER = 2
MLINESTYLE_START_SQARE = 16
MLINESTYLE_START_INNER_ARC = 32
MLINESTYLE_START_ROUND = 64
MLINESTYLE_END_SQUARE = 256
MLINESTYLE_END_INNER_ARC = 512
MLINESTYLE_END_ROUND = 1024
